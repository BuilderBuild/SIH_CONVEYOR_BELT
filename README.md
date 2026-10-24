# ConveyX — conveyor belt inspection prototype

ConveyX uses the existing single-class YOLO26n checkpoint to highlight candidate physical belt damage. It supports image inspection, sequential video processing, local camera monitoring, SQLite history, software alerts and saved model evaluation reports. Human review is required: the baseline misses damage and can produce false alarms. It does not control a conveyor motor.

The original documentation is preserved in `docs/README.original.md`. Original preparation/training scripts, images, annotations and model checkpoints remain in place. See `PROJECT_STATUS.md` for inspection findings, remaining limitations and feature status.

For protected public access hosted from this PC, see `PC_HOSTING.md` and `PUBLIC_HOSTING_STATUS.md`. `share-local.ps1` requires allowed-email authentication; `stop-sharing.ps1` stops the tracked background tunnel. Public access uses the PC's existing application/GPU/storage and requires the PC to remain online. Authenticated external checks are recorded separately from local tests.

## Continued verification and clean dataset

The approved continuation created `dataset_detection_verified_v2` as a separate copy: **112 train, 31 validation and 19 test images**, with all **627 defect boxes** retained. Its audit passes with no exact duplicates or cross-split leakage. All retained files stay in their original splits; source images, labels and YAML are unchanged. The held-out test membership and contents are preserved. The four excluded files are normal-image duplicates: train/normal_11.jpeg, train/normal_84.jpeg, train/normal_86.jpeg and val/normal_83.jpeg. The validation copy was excluded because its identical training counterpart had already been seen by the historical baseline.

`dataset_detection_verified_v2/manifest.json` records every source hash, copied file and exclusion. `audit.json` records the independent result. Reproduce to a **new** destination with:

```powershell
python -m src.dataset_derivation --destination dataset_detection_verified_another_copy
python -m src.dataset_validator dataset_detection_verified_v2/data.yaml --report outputs/reports/verified_v2_audit.json
python -m src.evaluation --data dataset_detection_verified_v2/data.yaml --device cpu
```

Baseline versus last-checkpoint comparison on the same clean validation data at 640 pixels confirms best.pt remains stronger: mAP50–95 **.09498** versus **.08213**. Evaluating best.pt at 960 pixels gave **.07181**, so a larger inference size is not assumed better. Model comparison now has a reproducible CLI that rejects test reports, different dataset fingerprints/sizes/devices, audit failures and changed checkpoints:

```powershell
python -m src.model_selection path/to/first/evaluation.json path/to/second/evaluation.json --output outputs/reports/comparison.json
# Only after reviewing comparable validation evidence, explicitly add --select.
```

Training now saves a unique JSON provenance/progress report with source checkpoint hash, train/validation fingerprint, per-epoch metrics, completion/failure status and the saved checkpoint location. Tests verify unique output experiments and propagation of training errors.

## Launch on this computer

From PowerShell:

```powershell
Set-Location D:\Conveyor_dataset
.\launch-gpu.ps1
```

Open [ConveyX](http://127.0.0.1:8502). Stop the server with Ctrl+C in its terminal. The GPU launcher uses the approved `.venv-conveyx-gpu` interpreter. `launch.ps1` remains the CPU fallback using `E:\PYTHON\python.exe` (Python 3.14.4). Both use the project-local Streamlit dependencies under `outputs/runtime`; the existing Python installation and empty `.venv` were not replaced. To specify the original CPU interpreter or another port:

```powershell
.\launch.ps1 -Python E:\PYTHON\python.exe -Port 8503
```

If PowerShell blocks local scripts, run these commands directly without changing execution policy:

```powershell
Set-Location D:\Conveyor_dataset
$env:PYTHONPATH = "$PWD\outputs\runtime"
$env:YOLO_CONFIG_DIR = "$PWD\outputs\yolo_config"
python -m streamlit run app.py
```

`app.py` exists and both its seven pages and the local HTTP server have been tested. In a separately installed environment, `streamlit run app.py` is the equivalent entry point. The existing `.venv` is not a working environment for this app.

## Architecture

```text
app.py                         Streamlit dashboard; display and user actions
config.yaml                    Defaults; persisted overrides in outputs/settings.json
src/inference.py               Dashboard-independent YOLO engine and structured results
src/model_manager.py           Explicit checkpoint validation, SHA256 identity, device checks
src/image_processing.py        Annotated images, JSON and inspection persistence
src/video_processing.py        Bounded frame memory, encoded video, frame/event JSONL
src/camera.py                  Camera worker, stop/release, duration and heartbeat limits
src/alerts.py                  Consecutive-hit, IoU-matched candidate alert tracks
src/database.py                SQLite inspections and alerts; idempotent IDs
src/dataset_validator.py       Read-only labels, paths, duplicate/leakage audit
src/training.py                Configurable training in a unique experiment directory
src/evaluation.py              Real metrics, PR curves, confusion matrices, error analysis
src/cli.py                     Headless image/video inspection
tools/verify_prototype.py      Real image/video/database benchmark; optional real camera
tools/inspect_workspace.py     Artifact inventory and confirmed CVAT comparison
tests/                         Automated tests, including Streamlit AppTest
outputs/                       Uploaded inputs, annotated media, SQLite, reports, runtime
```

Services accept arrays/paths and structured results without Streamlit. A future camera adapter can supply BGR frames to `DetectionEngine.detect()`. Database records use UTC timestamps and SHA256 model versions. Run IDs and output names are unique; checkpoints are never overwritten by the new training command.

## Environment and installation elsewhere

The tested CPU environment has Python 3.14.4, torch 2.12.0+cpu, Ultralytics 8.4.184, OpenCV 4.13.0 and Streamlit 1.66.1. Internet is needed only for dependency/model downloads, not local inspections. Supply trusted local checkpoints; the engine does not automatically download models.

For a new CPU environment, use a **new** directory rather than replacing an existing environment:

```powershell
python -m venv .venv-conveyx
.\.venv-conveyx\Scripts\python.exe -m pip install -r requirements.txt
.\launch.ps1 -Python .\.venv-conveyx\Scripts\python.exe
```

`requirements.txt` describes supported dependency ranges; `requirements-tested.txt` captures the direct package versions used for final verification. Native video encoders depend on the installed OpenCV build. Project-local runtime dependencies include a newer protobuf than some unrelated global Google packages support; they are used only in the dashboard process. Use a dedicated environment for other applications.

### Approved GPU environment

The RTX 5050 Laptop GPU is visible with 8151 MiB VRAM and NVIDIA driver 610.74. The original system torch remains CPU-only. The user approved a separate `.venv-conveyx-gpu` environment; it now contains torch **2.12.0+cu130** and torchvision **0.27.0+cu130**. It inherits existing supporting packages read-only through `--system-site-packages`, but its CUDA torch/torchvision are installed locally and do not replace the CPU packages.

Actual CUDA matrix execution and real-checkpoint image inference passed. On one real validation image at 640 pixels, 12 warm full detect calls (including image decoding, annotation and synchronization) had medians of **42.0 ms CPU** and **24.4 ms GPU** in this environment. These differ from the earlier CPU-only benchmark context and are not camera FPS guarantees. Raw samples, hardware architecture and GPU memory measurements are in `outputs/reports/gpu_verification.json`.

```powershell
.\launch-gpu.ps1
# Or another port if the CPU dashboard is still running:
.\launch-gpu.ps1 -Port 8503
# Repeat the actual CUDA verification/benchmark:
.\.venv-conveyx-gpu\Scripts\python.exe tools/verify_gpu.py
```

Default `device: auto` uses CUDA in the GPU environment and CPU in the original environment. An explicitly saved device setting takes precedence. `launch.ps1` still supports the original CPU interpreter; `launch-gpu.ps1` verifies CUDA before starting the dashboard.

For GPU work, create a separate environment with a supported Python version and a matching CUDA-enabled torch/torchvision pair. The [official PyTorch version guide](https://pytorch.org/get-started/previous-versions/) lists torch 2.12.0 / torchvision 0.27.0 CUDA 13.0 wheels. The [PyTorch 2.12 release notes](https://pytorch.org/blog/pytorch-2-12-release-blog/) recommend CUDA 13.0+ for Blackwell GPUs and give a Windows minimum driver of 580.88. This machine's reported driver exceeds that version; actual installation and execution still require verification.

The official wheel versions used in the approved GPU environment can be reproduced there with:

```powershell
# After creating and activating the new environment:
python -m pip install --ignore-installed --no-deps torch==2.12.0+cu130 torchvision==0.27.0+cu130 --index-url https://download.pytorch.org/whl/cu130
python -m pip install -r requirements.txt
python -c "import torch; print(torch.__version__, torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
```

Only the separate environment was changed. CUDA Toolkit or driver installation is not part of the prototype work.

## Corrected dataset and preparation

The owner identified `CVAT_DETECTED_YOLO` as the corrected source. Independent comparison verified all 79 CVAT label files match the active `dataset_detection` defect labels, and all 79 corresponding images match `Images/defected` byte-for-byte. There are 627 structurally valid boxes and 87 explicit empty normal labels.

| Split | Images | Defect images | Empty normal labels | Boxes |
|---|---:|---:|---:|---:|
| Train | 115 | 55 | 60 | 453 |
| Validation | 32 | 15 | 17 | 116 |
| Test | 19 | 9 | 10 | 58 |

Use `dataset_detection/data.yaml`, with `0: defect`. The root `data.yaml` describes an obsolete three-class setup. `dataset_detection_backup` has no annotations and its YAML incorrectly refers to the active dataset. Neither is a valid independent corrected training source. CVAT exports reference original image names but do not themselves contain the complete split dataset.

**Known original leakage:** `images/train/normal_9.jpeg` and `images/val/normal_83.jpeg` are identical. Three further duplicate pairs exist within training. The original dataset is unchanged and still fails audit. The approved `dataset_detection_verified_v2` copy resolves exact duplication and is the supported training/evaluation source. Do not delete originals or silently reassign images. Structural validation does not prove that every annotated region represents physical damage; shadows, wrinkles, reflections, markings and normal texture still require visual review.

Read-only commands:

```powershell
python tools/inspect_workspace.py
python -m src.dataset_validator dataset_detection/data.yaml --report outputs/reports/dataset_audit.json
```

The validator checks YAML resolution, all three splits, readable images, explicit labels, class IDs, finite normalized box coordinates, box bounds, duplicate boxes/stems, orphan labels, normal-name labels, byte/decoded duplicates and cross-split perceptual similarity candidates. Exit code 1 is expected for the current dataset because of the confirmed leakage. Perceptual similarity is a review aid, not proof of leakage. It does not automatically correct annotations or splits.

## Training and model selection

The approved continuation completed one **100-epoch GPU training experiment** at 960 pixels, batch 8, seed 42 and patience 20, using the corrected labels and deduplicated dataset unchanged. It saved new best.pt and last.pt under `runs/detect/conveyx_20261024T025608_1e622a05/weights/`. Training took 691 seconds. An initial attempt failed before epoch 1 because of native YAML resolution; that issue is fixed and its failure log is preserved.

All four original/new checkpoints were evaluated at both 640 and 960 on the same clean validation split and GPU. The new last.pt at 640 ranked highest by mAP50–95 (.10327 versus .09474 for the original best.pt), but at the actual .25 operating threshold it had the same TP 32/FN 84 with **45 FP versus 40**. The original best.pt therefore remains the dashboard default. This is a deliberate deployment review, not automatic promotion of a new checkpoint. Detailed comparisons and the operating-point guard are in `outputs/reports/review_conveyx_20261024T025608_1e622a05/selection.json` and `outputs/model_selection.json`.

Semantic annotation review is recommended before additional training; see `ANNOTATION_REVIEW.md`. More epochs did not remove the label/localization ambiguity. Generic pretrained and classification checkpoints remain excluded from dashboard inference choices.

The derived dataset already passes audit. For a future justified experiment after further review:

```powershell
.\.venv-conveyx-gpu\Scripts\python.exe -m src.training --data dataset_detection_verified_v2/data.yaml --checkpoint yolo26n.pt --epochs 100 --batch 8 --image-size 960 --device 0 --patience 20 --confirmed-annotations
```

Training uses Windows-compatible zero workers, early stopping, seed 42 and a unique `runs/detect/conveyx_<timestamp>_<id>` directory. Ultralytics saves training logs, charts, `best.pt` and `last.pt`. The confirmation flag acknowledges annotation provenance and near-duplicate review; it does not bypass failed audit checks. Training writes a resolved runtime YAML so native Ultralytics uses the same paths as the validator. The full GPU training path, unique experiment handling, failure persistence and progress reporting have been tested.

## Evaluation and confidence analysis

The default is validation, with explicit opt-in required for final test evaluation:

```powershell
# Default: clean derived validation data
python -m src.evaluation --device cpu
# Historical original dataset diagnostics, explicitly qualified
python -m src.evaluation --data dataset_detection/data.yaml --allow-leakage
# Only after all tuning/model selection is finished:
python -m src.evaluation --data path/to/approved/data.yaml --split test --final-test
```

Evaluation copies the requested split into a unique output directory so Ultralytics caches cannot modify the original dataset. Each report stores dataset fingerprint, model hash, split, image size, actual precision/recall/mAP, threshold-specific TP/FP/FN, per-image ground truth and predictions, green/orange comparisons, PR curves and confusion matrices. Match analysis uses one-to-one greedy confidence ordering at box IoU 0.5. Compare models only on matching dataset fingerprints, splits and sizes. Saved reports appear in **Model performance**; no metrics are fabricated.

Measured validation baseline on 24 October 2026: precision **0.3374**, recall **0.4052**, mAP50 **0.2675**, mAP50–95 **0.0950**. Leakage can make these estimates optimistic. At confidence .25 and explicit overlap suppression, the diagnostic analysis finds 32 true positives, 40 false positives and 84 false negatives across 116 ground-truth boxes. No false positives occurred on the 17 validation normal images at that threshold; the 40 unmatched predictions were on defect images. This is not evidence of general immunity to shadows or markings.

The user-provided historical held-out test metrics (.385/.389/.298/.108) remain labeled historical. After validation-only model selection finished, the continuation ran one final evaluation of the retained baseline on the preserved 19-image test split: precision **.38707**, recall **.39203**, mAP50 **.29869**, mAP50–95 **.10780**. No tuning or model changes followed those results. Earlier legacy scripts used test images repeatedly, so a future genuinely unseen acquisition set is recommended for deployment qualification.

## Image inspection

Choose **Image inspection**, upload JPG/JPEG/PNG, preview, then select **Run detection**. The app saves the input, draws boxes/confidences, displays candidate region count and inference time, saves an inspection, and offers annotated-image/JSON/CSV downloads. There is a 40-megapixel image limit and configurable upload limit capped at 200 MB. A no-detection message always retains the model limitation.

Headless use, with a real local path:

```powershell
python -m src.cli image dataset_detection/images/val/defected_13.jpeg
```

## Video inspection

Choose **Video inspection**, upload a supported video and select **Process video**. MP4, AVI, MOV, MKV and M4V are accepted where codecs support them. Frames are decoded one at a time; the entire decoded video is never kept in RAM. Streamlit itself buffers compressed uploads within the upload cap. Progress, annotated video download, per-frame JSONL detections and temporally filtered candidate event timestamps are provided. Event frames are saved and indexed in SQLite.

Videos try H.264, then MP4V, then MJPEG/AVI. Browser playback depends on encoding; download and use a local player if necessary. Audio is not preserved. The processing button runs a bounded-memory job synchronously; do not navigate away while it is running. Outputs above 200 MB skip browser preview/download and are provided as local paths instead of being buffered into the browser. Large local input videos can use the CLI:

```powershell
python -m src.cli video path/to/belt_video.mp4
```

The real-checkpoint smoke video consists of 12 repeated frames from a real project image. Real moving-conveyor videos, long-duration processing and all possible codecs remain to be validated.

## Live camera monitoring

Choose **Live camera**, enter a local camera index, then **Start camera** and **Stop camera**. A worker thread owns capture and YOLO inference; a Streamlit fragment displays frames and measured processing FPS. The camera releases on stop, navigation, errors, duration expiry (default 120 seconds), or missing UI heartbeat for 15 seconds. Closing a tab is detected by heartbeat rather than an immediate browser close callback. A stalled native driver may delay release; the app reports a worker that fails to stop.

Camera 0 was actually opened/read/released and a five-second camera+YOLO worker smoke test processed five frames, stopped without errors, and stored a session summary. After the Windows watcher fix, browser monitoring sessions processed 194 and 267 frames, with live preview and start/stop verified and a healthy server afterward. This validates local camera plumbing, not belt damage recognition on a live conveyor. Other camera indexes, industrial SDKs and network cameras are not verified.

Every processed camera frame is logged to JSONL. Candidate snapshots and temporally filtered alert frames are saved. Session summaries and alert frames appear in history. Temporal matching requires consecutive frames and matches boxes by IoU, emitting one alert per spatial track until expiry. Motion, occlusion or re-entry can create new tracks. Track/event counts never claim unique confirmed physical defects.

## History, alerts and settings

SQLite is stored at `outputs/conveyx.sqlite3`. `inspections` stores IDs, UTC timestamp, input/output references, model SHA256, candidate count, confidence scores, processing time, status and full JSON payload. `alerts` links to inspections. Primary-key idempotence prevents duplicate writes when the same result is stored again. Dashboard reruns do not rerun inspection buttons. History filters by status, input type and ISO timestamp; select a record to view/download its output. Missing or moved output files produce a clear warning.

Statuses are `candidate_defect`, `no_defect_detected`, `processing_error` and `camera_disconnected`. Candidate alerts are software warnings only. Settings persist model path, confidence, IoU, image size, max detections, device, output folder, temporal filtering and upload/session limits. Selected checkpoints are loaded and class/task-validated before saving. Settings apply to subsequent inspections; navigate to refresh after saving.

Overview counters come from the actual database, including clearly labeled smoke records. Video/camera session counts indicate presence (0/1); event-frame observations and summaries are separate records, so aggregates are **not unique physical defect counts**. Alert IDs and candidate region counts serve different purposes. The prototype is intended for one local operator and binds to loopback; multi-user access control is not implemented.

## Tests and performance

```powershell
# This machine's local Streamlit runtime:
$env:PYTHONPATH = "$PWD\outputs\runtime"
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
python -m pytest -q --junitxml=outputs/reports/tests.xml
python tools/verify_prototype.py
# Explicitly include physical camera capture:
python tools/verify_prototype.py --camera
```

Tests cover label validity/coordinate conversion, dataset audit and leakage, trusted checkpoint loading, real image inference, serialization, SQLite idempotence/retrieval/filtering, temporal alerts, one-to-one matching, invalid images/videos/configuration, actual generated-video encoding/decoding, mocked camera failures/release and all seven dashboard pages. Test fixtures use temporary databases; the smoke command writes labeled real records to the main database.

Final continuation verification: **51 passed in the CPU environment and 51 passed in the CUDA environment**, with zero failures/errors/skips and one upstream pandas deprecation warning per run. Two additional final dashboard checks passed after adding the deployment-review display. Tests use a new directory under `outputs/test_runs` on each run to avoid Windows account-specific temporary-folder ownership conflicts. `TEST_REPORT.md` lists the test cases and environments.

The initial CPU-only smoke had a warm median of **24.9 ms** across eight repeats of one 720×1280 validation image at model size 640; cold first prediction was about **2162 ms**, and process RSS snapshots were about 216 to 448 MiB (not peak). The later synchronized comparison in the CUDA environment, including image decoding/annotation, measured medians **42.0 ms CPU / 24.4 ms GPU**. A separate GPU image/video/database/camera smoke passed with **115 camera frames**, clean stop/release and a last measured processing rate of **35.9 FPS**. These are specific smoke conditions, not guaranteed conveyor throughput. Raw reports are `prototype_smoke.json`, `gpu_verification.json` and `prototype_gpu_smoke.json` under outputs/reports.

## Troubleshooting and limitations

- Missing Streamlit: use `launch.ps1` on this machine, or install requirements into a separate environment. Do not activate the old empty `.venv`.
- CUDA error: select `cpu`; a visible NVIDIA GPU alone does not make a CPU-only torch build CUDA-capable.
- Checkpoint class/task error: choose the trained single-class detection checkpoint, not the classification or generic COCO checkpoint.
- Invalid dataset: inspect JSON audit errors. Do not use root data.yaml or the image-only backup for training.
- Camera unavailable: close other camera applications, verify Windows camera permissions, and try the correct camera index. The local server accesses this PC's camera.
- Video encoding warnings: fallback encoders are tried and errors remain visible; a local player may be needed for MP4V/AVI.
- Database/path errors: ensure configured folders are writable and output files have not been moved. Copy SQLite backups while the server is stopped.
- No detection: inspect lighting, framing and confidence, then review the actual image. Do not infer a guaranteed healthy belt.
- Model quality: low recall/localization accuracy, small data, possible scene similarity, annotation ambiguity and historical test reuse prevent production acceptance. Exact duplicate leakage was resolved only in the derived copy. One controlled retraining experiment completed; no annotations were automatically changed. See ANNOTATION_REVIEW.md before further training.
- Dependency warning: Streamlit's current chart helper emits a pandas deprecation warning; functional tests pass.
- Source watching is disabled in `.streamlit/config.toml`: the Windows/Python 3.14 watcher created many threads and crashed during browser verification. Restart the server after source edits. The fixed server uses port 8502 because a crashed test process retained port 8501. Use `-Port 8503` if the chosen port is occupied. No system Python or driver changes were made.

## Future hardware integration

USB camera support and the inference API are modular. Industrial camera SDK adapters, Raspberry Pi runtime/export and sensors can supply frames/metadata later. Raspberry Pi performance, PLC integration, microcontroller protocols and industrial monitoring exports are not implemented or certified. Automatic shutdown/motor/PLC control requires a separately requested, validated hardware safety design.
