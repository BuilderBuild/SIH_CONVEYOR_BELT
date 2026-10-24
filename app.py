"""ConveyX local monitoring dashboard. Run through launch.ps1 or streamlit."""
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import uuid

import cv2
import numpy as np
import pandas as pd
from PIL import Image
import streamlit as st
import torch

from src.config import ROOT, load_settings, resolve, save_settings
from src.database import Database
from src.inference import DetectionEngine, Inspection
from src.model_manager import checkpoints, model_info, LIMITATIONS
from src.image_processing import inspect_image
from src.video_processing import process_video
from src.camera import CameraMonitor
from src.alerts import make_event

st.set_page_config(page_title="ConveyX | Belt monitoring", page_icon="⚙", layout="wide")
st.markdown("""<style>.block-container {padding-top:2rem} h1 {letter-spacing:-1px}
div[data-testid="stMetric"] {background:#141f30; padding:18px; border-radius:10px;
border-top:2px solid #f7a928} .stCaption {color:#97a9c0}</style>""", unsafe_allow_html=True)


@st.cache_resource
def get_engine(path, version, confidence, iou, size, maximum, device):
    return DetectionEngine(path, confidence, iou, size, maximum, device)


def engine_for(settings):
    info = model_info(settings["model"])
    return get_engine(info["path"], info["version"], settings["confidence"], settings["iou"],
                      settings["image_size"], settings["max_detections"], settings["device"])


def show_download(path, label, key):
    path = Path(path)
    if not path.is_file():
        st.warning(f"Output is unavailable: {path}")
    elif path.stat().st_size <= 200 * 1024**2:
        with path.open("rb") as stream:
            st.download_button(label, stream, file_name=path.name, key=key)
    else:
        st.info(f"Output exceeds the 200 MB browser download limit. Open locally: {path}")


def persist_upload(upload, settings):
    if upload.size > settings["max_upload_mb"]*1024**2:
        raise ValueError(f"Upload exceeds the configured {settings['max_upload_mb']} MB limit.")
    target = resolve(settings["output_directory"]) / "uploads" / (uuid.uuid4().hex + Path(upload.name).suffix.lower())
    target.parent.mkdir(parents=True, exist_ok=True)
    upload.seek(0)
    with target.open("xb") as stream:
        while chunk := upload.read(1024**2):
            stream.write(chunk)
    upload.seek(0)
    return target


def failure(exc, reference, kind, database, settings):
    st.error(f"Processing error: {type(exc).__name__}: {exc}")
    info = model_info(settings["model"])
    result = Inspection(uuid.uuid4().hex, datetime.now(timezone.utc).isoformat(), str(reference), info["version"],
                        info["name"], [], 0, "processing_error", error=str(exc), kind=kind)
    try:
        database.record(result, [make_event(result)])
    except Exception as db_error:
        st.error(f"Could not persist the error record: {db_error}")


def result_view(data):
    st.caption(f"Inspection {data['id']} | {data['input_reference']} | model {data['model_version'][:12]}")
    if data["status"] == "candidate_defect":
        st.warning("Candidate belt damage detected. Review the marked regions before taking action.")
    elif data["status"] == "no_defect_detected":
        st.info("No candidate defect detected at the selected threshold. This does not guarantee a defect-free belt.")
    else:
        st.error(data.get("error") or data["status"])
    cols = st.columns(3)
    cols[0].metric("Candidate regions", data["detection_count"])
    cols[1].metric("Inference time", f"{data['processing_ms']:.1f} ms")
    cols[2].metric("Peak confidence", f"{max(data['confidence_scores'], default=0):.1%}")
    output = Path(data.get("output_reference", ""))
    if output.is_file() and output.suffix.lower() in (".jpg", ".jpeg", ".png"):
        st.image(str(output), caption="Saved annotated inspection", width="stretch")
        show_download(output, "Download annotated image", "img_"+data["id"])
    st.dataframe(pd.DataFrame(data["detections"]), width="stretch")
    left, right = st.columns(2)
    left.download_button("Export JSON", json.dumps(data, indent=2), file_name=f"{data['id']}.json", mime="application/json")
    rows = [{"inspection_id": data["id"], "status": data["status"], "model_version": data["model_version"],
             **d, "xyxy": json.dumps(d["xyxy"])} for d in data["detections"]]
    if not rows:
        rows = [{"inspection_id": data["id"], "status": data["status"], "model_version": data["model_version"]}]
    right.download_button("Export CSV", pd.DataFrame(rows).to_csv(index=False), file_name=f"{data['id']}.csv", mime="text/csv")


def performance():
    selection_path = resolve("outputs/model_selection.json")
    if selection_path.is_file():
        selection = json.loads(selection_path.read_text(encoding="utf-8"))
        operating = selection.get("operating_point_review")
        if operating:
            st.info("Latest deployment review: " + operating["reason"])
            st.caption(f"Operating confidence {operating['confidence']:.2f}. "
                       f"Baseline FP/FN: {operating['baseline']['FP']}/{operating['baseline']['FN']}; "
                       f"candidate FP/FN: {operating['candidate']['FP']}/{operating['candidate']['FN']}. "
                       "These are box-level comparisons, not counts of unique physical defects.")
    reports = sorted(resolve("outputs/reports").glob("evaluation_*/evaluation.json"), reverse=True)
    if not reports:
        st.info("No evaluation reports saved. Run python -m src.evaluation on the verified derived dataset.")
    else:
        records = [json.loads(p.read_text(encoding="utf-8")) for p in reports]
        st.dataframe(pd.DataFrame([{"model": r["model"]["name"], "version": r["model"]["version"][:12],
                                    "split": r["split"], "data_hash": r["dataset_fingerprint"][:12],
                                    "image_size": r["image_size"], "device": r["device"], **r["metrics"]} for r in records]), width="stretch")
        choice = st.selectbox("Saved evaluation", range(len(records)), format_func=lambda i: f"{records[i]['timestamp']} | {records[i]['model']['name']} | {records[i]['split']}")
        report = records[choice]
        st.warning(report["qualification"])
        st.caption(report["comparison_policy"])
        cols = st.columns(4)
        for col, (key, value) in zip(cols, report["metrics"].items()):
            col.metric(key, f"{value:.3f}")
        st.dataframe(pd.DataFrame(report["threshold_analysis"]), width="stretch")
        for plot in ("BoxPR_curve.png", "confusion_matrix.png", "confusion_matrix_normalized.png"):
            path = Path(report["plots_directory"]) / plot
            if path.is_file():
                st.image(str(path), caption=plot)
        comparisons = sorted((reports[choice].parent / "comparisons").glob("*.jpg"))
        if comparisons:
            selected = st.selectbox("Ground truth (green) / predictions (orange)", comparisons, format_func=lambda p: p.name)
            st.image(str(selected))
        show_download(report["error_analysis"], "Download false-positive / false-negative analysis", "errors")
        show_download(reports[choice], "Download evaluation JSON", "evaluation")
    with st.expander("Original training validation history"):
        csv = ROOT / "runs/detect/conveyor_defect_v1/results.csv"
        if csv.is_file():
            frame = pd.read_csv(csv)
            frame.columns = frame.columns.str.strip()
            columns = [c for c in frame.columns if c.startswith("metrics/")]
            st.line_chart(frame.set_index("epoch")[columns])
            st.caption("Original per-epoch validation results; these are not held-out test results.")
    st.caption("User-reported historical test baseline: precision .385, recall .389, mAP50 .298, mAP50-95 .108. Fresh validation and final-test reports are listed above with their split and model version.")


def settings_page(settings):
    with st.form("settings"):
        available = checkpoints()
        current = settings["model"]
        if current not in available:
            available.insert(0, current)
        model = st.selectbox("Trusted detection checkpoint", available, index=available.index(current))
        custom = st.text_input("Or local trusted checkpoint path", "")
        confidence = st.slider("Confidence threshold", .01, 1.0, float(settings["confidence"]), .01)
        iou = st.slider("Overlap suppression IoU", .05, 1.0, float(settings["iou"]), .05)
        size = st.number_input("Image size (multiple of 32)", 32, 2048, int(settings["image_size"]), 32)
        maximum = st.number_input("Maximum detections", 1, 1000, int(settings["max_detections"]))
        device = st.text_input("Device (cpu, auto, or CUDA index)", str(settings["device"]))
        output = st.text_input("Output directory", settings["output_directory"])
        enabled = st.checkbox("Candidate alerts", value=settings["alerts_enabled"])
        hits = st.number_input("Consecutive frames before camera/video alert", 1, 100, settings["alert_hits"])
        match_iou = st.slider("Temporal matching IoU", .05, 1.0, float(settings["alert_match_iou"]), .05)
        expiry = st.number_input("Track expiry after absence (seconds)", .1, 60.0, float(settings["alert_expiry_seconds"]))
        duration = st.number_input("Maximum camera session (seconds)", 1, 3600, settings["camera_max_seconds"])
        upload = st.number_input("Upload limit MB (server cap 200)", 1, 200, settings["max_upload_mb"])
        if st.form_submit_button("Validate and save settings"):
            updated = {**settings, "model": custom.strip() or model, "confidence": confidence, "iou": iou,
                       "image_size": int(size), "max_detections": int(maximum), "device": device.strip(),
                       "output_directory": output, "alerts_enabled": enabled, "alert_hits": int(hits),
                       "alert_match_iou": match_iou, "alert_expiry_seconds": expiry,
                       "camera_max_seconds": int(duration), "max_upload_mb": int(upload)}
            try:
                engine_for(updated)
                resolve(output).mkdir(parents=True, exist_ok=True)
                save_settings(updated)
                st.success("Settings saved; the selected checkpoint was loaded and validated.")
            except Exception as exc:
                st.error(f"Settings were not saved: {exc}")
    st.caption("Model selection is explicit. No checkpoint is promoted solely because it is newer. Select only trusted local PyTorch files.")


try:
    settings = load_settings()
    database = Database(resolve(settings["database"]))
except Exception as exc:
    st.error(f"Startup configuration/database error: {exc}")
    st.stop()

page = st.sidebar.radio("Workspace", ["Overview", "Image inspection", "Video inspection", "Live camera", "Detection history", "Model performance", "Settings"])
st.sidebar.markdown("### ConveyX\nConveyor belt condition monitoring")
st.sidebar.caption(f"Confidence {settings['confidence']:.2f} | IoU {settings['iou']:.2f} | {settings['device']}")
st.title("ConveyX")
st.caption("AI-POWERED CONVEYOR BELT INSPECTION  /  LOCAL PROTOTYPE")
st.warning(LIMITATIONS)

monitor = st.session_state.get("camera_monitor")
if page != "Live camera" and monitor and monitor.running:
    try:
        monitor.stop()
    except RuntimeError as exc:
        st.error(str(exc))

if page == "Overview":
    st.subheader("Operations overview")
    try:
        with st.spinner("Verifying detection engine..."):
            engine = engine_for(settings)
        st.success(f"AI engine ready | {engine.info['name']} | device {engine.device}")
        st.caption(f"Checkpoint SHA256: {engine.info['version']}")
    except Exception as exc:
        st.error(f"AI engine unavailable: {exc}")
    st.write(f"PyTorch {torch.__version__} | CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        st.caption(f"CUDA GPU: {torch.cuda.get_device_name(0)} | build {torch.version.cuda}")
    stats = database.stats()
    for col, label, key in zip(st.columns(3), ["Stored inspection records", "Records with candidate regions", "Stored region observations"], stats):
        col.metric(label, stats[key])
    st.caption("Video event frames and video summaries are separate records. Region observations are not counts of unique physical defects. Demonstration records may be included.")
    st.subheader("Recent software alerts")
    alerts = database.alerts()
    if alerts:
        st.dataframe(pd.DataFrame(alerts), width="stretch")
    else:
        st.info("No stored alerts.")
    st.subheader("Recent inspection history")
    history = database.history(limit=10)
    st.dataframe(pd.DataFrame([{k: row.get(k) for k in ("id", "timestamp", "kind", "status", "detection_count", "input_reference")} for row in history]), width="stretch")
    reports = sorted(resolve("outputs/reports").glob("evaluation_*/evaluation.json"), reverse=True)
    if reports:
        report = json.loads(reports[0].read_text(encoding="utf-8"))
        st.subheader("Latest saved evaluation")
        st.write({"model": report["model"]["name"], "split": report["split"], **report["metrics"]})
        st.caption(report["qualification"])

elif page == "Image inspection":
    st.subheader("Image defect detection")
    upload = st.file_uploader("Belt image", type=["jpg", "jpeg", "png"])
    if upload:
        try:
            if upload.size > settings["max_upload_mb"]*1024**2:
                raise ValueError("Image exceeds configured upload limit.")
            with Image.open(upload) as preview:
                if preview.width*preview.height > 40_000_000:
                    raise ValueError("Image exceeds the 40-megapixel inspection limit.")
                preview.verify()
            upload.seek(0)
            st.image(upload, caption=upload.name, width="stretch")
            if st.button("Run detection", type="primary"):
                source = persist_upload(upload, settings)
                with st.spinner("Inspecting belt image..."):
                    result, _ = inspect_image(engine_for(settings), source, resolve(settings["output_directory"]),
                                              database, settings["alerts_enabled"])
                st.session_state["last_image_result"] = result.to_dict()
        except Exception as exc:
            failure(exc, upload.name, "image", database, settings)
    if "last_image_result" in st.session_state:
        result_view(st.session_state["last_image_result"])

elif page == "Video inspection":
    st.subheader("Video defect detection")
    st.caption("Frames are decoded sequentially. Uploads are capped at 200 MB; the CLI accepts larger local videos. Audio is not copied. Codec availability varies.")
    upload = st.file_uploader("Belt video", type=["mp4", "avi", "mov", "mkv", "m4v"])
    if upload and st.button("Process video", type="primary"):
        try:
            source = persist_upload(upload, settings)
            bar = st.progress(0, text="Preparing video...")
            def progress(done, total):
                bar.progress(min(1., done/total) if total else 0, text=f"Processed {done} / {total or '?'} frames")
            result = process_video(engine_for(settings), source, resolve(settings["output_directory"]), database, progress,
                                   settings["alerts_enabled"], settings["alert_hits"], settings["alert_match_iou"], settings["alert_expiry_seconds"])
            bar.progress(1., text="Video complete")
            st.session_state["last_video"] = {"inspection": result.inspection.to_dict(), "frames": result.frames,
                                              "events": result.event_count, "frame_log": result.frame_log,
                                              "events_file": result.events_file}
        except Exception as exc:
            failure(exc, upload.name, "video", database, settings)
    if "last_video" in st.session_state:
        result = st.session_state["last_video"]
        data = result["inspection"]
        if data["detection_count"]:
            st.warning("Candidate damage present; review output.")
        else:
            st.info("No candidate damage detected. Human review is still needed.")
        st.write(f"{result['frames']} frames | {result['events']} temporally filtered candidate events | {data['processing_ms']/1000:.1f} seconds processing")
        output = Path(data["output_reference"])
        if output.suffix == ".mp4" and output.stat().st_size <= 200 * 1024**2:
            st.video(str(output))
            st.caption("If your browser cannot decode this MP4, download and play it locally.")
        show_download(output, "Download annotated video", "video_download")
        show_download(result["frame_log"], "Download frame detection logs", "frame_log")
        show_download(result["events_file"], "Download candidate event timestamps", "event_log")

elif page == "Live camera":
    st.subheader("Live camera monitoring")
    st.caption("Camera indexes refer to this Windows PC. Sessions stop on navigation, after the configured duration, or after 15 seconds without dashboard heartbeat. Spatial matching reduces repeats; moving or returning damage may produce another event.")
    index = st.number_input("USB / local camera index", min_value=0, max_value=20, value=0)
    left, right = st.columns(2)
    if left.button("Start camera", disabled=bool(monitor and monitor.running)):
        try:
            monitor = CameraMonitor(engine_for(settings), database, resolve(settings["output_directory"]), int(index),
                                    settings["camera_max_seconds"], settings["alerts_enabled"], settings["alert_hits"],
                                    settings["alert_match_iou"], settings["alert_expiry_seconds"])
            st.session_state["camera_monitor"] = monitor
            monitor.start()
            st.rerun()
        except Exception as exc:
            failure(exc, f"camera:{index}", "camera", database, settings)
    if right.button("Stop camera") and monitor:
        try:
            monitor.stop()
            st.rerun()
        except RuntimeError as exc:
            st.error(str(exc))

    @st.fragment(run_every=.3)
    def live_preview():
        monitor = st.session_state.get("camera_monitor")
        if not monitor:
            st.info("Camera has not been started.")
            return
        frame, result, state, error, fps, events = monitor.snapshot()
        st.write(f"Status: {state} | measured processing FPS: {fps:.1f}")
        if error:
            st.error(error)
        if frame is not None:
            st.image(frame, channels="BGR", width="stretch")
        if result and result.detections:
            st.warning(f"Candidate regions: {result.detection_count}. Human review required.")
            st.write([round(d.confidence, 3) for d in result.detections])
        elif result:
            st.info("No candidate defect detected in the latest frame.")
        if events:
            st.dataframe(pd.DataFrame(events), width="stretch")
    live_preview()

elif page == "Detection history":
    st.subheader("Stored inspections")
    status = st.selectbox("Status", ["All", "candidate_defect", "no_defect_detected", "processing_error", "camera_disconnected"])
    kind = st.selectbox("Input type", ["All", "image", "video", "video_event", "camera", "camera_frame", "smoke_image"])
    since = st.text_input("From UTC timestamp (optional ISO 8601)", "")
    until = st.text_input("Through UTC timestamp (optional ISO 8601)", "")
    for value in (since, until):
        if value:
            try:
                datetime.fromisoformat(value)
            except ValueError:
                st.error("Use an ISO 8601 date/time, for example 2026-10-24T00:00:00+00:00.")
                st.stop()
    rows = database.history(None if status == "All" else status, None if kind == "All" else kind, since, until)
    st.caption("Showing at most 500 matching records; timestamps are stored in UTC.")
    if rows:
        st.dataframe(pd.DataFrame([{k: row.get(k) for k in ("id", "timestamp", "kind", "status", "detection_count", "processing_ms", "input_reference")} for row in rows]), width="stretch")
        selected = st.selectbox("View inspection", range(len(rows)), format_func=lambda i: f"{rows[i]['timestamp']} | {rows[i]['kind']} | {rows[i]['id'][:8]}")
        row = rows[selected]
        result_view(row)
        if row["kind"] == "video":
            show_download(row["output_reference"], "Download stored video", "history_video")
        st.download_button("Export filtered history JSON", json.dumps(rows, indent=2), "inspection_history.json")
    else:
        st.info("No matching inspection records.")

elif page == "Model performance":
    st.subheader("Verified model results")
    performance()

elif page == "Settings":
    st.subheader("Inference and alert settings")
    settings_page(settings)
