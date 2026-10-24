# ConveyX project status

Current continuation: approved GPU environment and exact-deduplicated dataset are verified; one 100-epoch experiment completed; 51 tests pass in each CPU/CUDA environment. The original best.pt remains selected because the new mAP-ranked candidate has more unmatched predictions at the actual operating threshold without reducing missed boxes. See `ML_COMPLETION_REPORT.md` and `ANNOTATION_REVIEW.md`.

Inspection: 24 October 2026. Original scripts, annotations and checkpoints are preserved.

## Initial findings

- Completed: original classification dataset and training; detection dataset builder with box validation; YOLO26n detection training; standalone prediction and held-out evaluation scripts.
- Partial: inference exists only as hardcoded scripts; dataset inspection does not check content duplicates; evaluation results are not stored in a dashboard-readable registry.
- Missing at inspection: dashboard, reusable inference API, SQLite history, software alerts, video/camera services, configuration, automated tests and launch procedure.
- Antigravity: no dashboard, frontend files or attribution identifying Antigravity-generated components were found. There were 13 root Python scripts at initial inspection; no additional application source outside the environment.
- Bugs/risks: root data.yaml incorrectly defines three classes; backup YAML points at the active dataset; legacy evaluation/tuning scripts use test images repeatedly; classification predict.py does not localize damage; scripts execute at import and use fixed Windows paths.
- Dataset: active detection dataset, image-only backup, CVAT exports and originals require content comparison. Corrected annotation provenance is not yet independently established. No training is authorized until this is resolved.
- Model: one detection experiment conveyor_defect_v1 with best.pt and last.pt; other trained checkpoints are classification models. Existing detection best.pt is the provisional baseline, not a production-qualified model. Historical held-out metrics supplied by user: P .385, R .389, mAP50 .298, mAP50-95 .108 (not newly measured).
- Dashboard: none exists initially; application startup is unavailable initially.
- Hardware: NVIDIA RTX 5050 with about 8 GiB VRAM is visible through nvidia-smi. E:/PYTHON/python.exe has torch 2.12.0+cpu, ultralytics 8.4.184, OpenCV 4.13.0; CUDA unavailable. .venv lacks these libraries. Streamlit is absent.

## Completion checklist / implementation order

- [x] Inspect existing files, scripts, checkpoints and environments.
- [x] Audit all dataset copies and compare annotations without altering them.
- [x] Add reusable image/video/camera inference and explicit model selection.
- [x] Add configuration, SQLite records and temporally filtered candidate alerts.
- [x] Add Streamlit overview, image, video, camera, history, performance and settings.
- [x] Add configurable training and validation-only evaluation tools.
- [x] Run automated tests, real image/video smoke tests, latency and dashboard launch checks.
- [x] Write final README, PowerShell launcher and feature status matrix.

No original dataset, label, checkpoint or legacy script will be replaced. README updates retain an original copy.

## Verified dataset/model findings

The owner confirmed CVAT_DETECTED_YOLO as the corrected annotation source during this session. All 79 source labels match active defect labels, all 79 corresponding image copies match original bytes, and all 627 boxes parse with class 0 and valid geometry. There are 87 explicit empty normal labels. Counts are train 115 images/453 boxes, val 32/116, test 19/58.

Read-only audit **fails** because train/normal_9.jpeg and val/normal_83.jpeg are identical. Three further duplicate pairs are within training. The sole perceptual cross-split similarity candidate is that same exact pair. No images were moved and no annotations were changed. The backup has zero labels and its YAML redirects to the active dataset. Root data.yaml has obsolete three-class names. See outputs/reports/annotation_provenance.json, dataset_detection_audit.json, dataset_detection_backup_audit.json and workspace_inventory.json.

The app explicitly uses conveyor_defect_v1/weights/best.pt, SHA256 110a1a54cd40f557e7f10386d3cf86239f0df21b96c6a722ea2e03bced274e54. The continuation independently compared both original and both new checkpoints at two image sizes; the baseline was retained after operating-point review. Classification and generic pretrained weights are rejected by the inference engine. Promotion requires matching validation conditions plus review of FP/FN at the configured threshold.

Initial original-dataset validation diagnostics: precision 0.337411, recall 0.405172, mAP50 0.267455, mAP50-95 0.094981. Leakage qualification is stored and displayed. At confidence .25 / matching IoU .5 the explicit-NMS analysis yields TP 32, FP 40, FN 84. None of the 17 original normal validation images has a false-positive box at this threshold; all unmatched predictions are on defect images. The continuation used the clean derived split for selection, then evaluated the retained baseline once on the preserved test split (P .38707, R .39203, mAP50 .29869, mAP50-95 .10780). No tuning followed final test evaluation; legacy scripts previously reused test data.

## Final feature classifications

| Feature | Status | Evidence and practical limit |
|---|---|---|
| Seven-page Streamlit dashboard and overview | Implemented and tested | All pages exercised with AppTest; browser rendering and loopback health verified. Final server on port 8502. |
| Image upload, reusable inference, boxes/confidences, JSON/CSV/image output | Implemented and tested | Real baseline checkpoint and real validation image; serialization and persistence round trip. Browser upload/download interaction is supplementary manual verification. |
| Video engine, progress, output, frame/event logs | Implemented and tested | Actual four-frame automated and 12-frame persistent smoke clips encoded/decoded. Clips derive from a real project image. Long videos and every codec/container are not fully tested. |
| Camera capture/inference, stop/release and error handling | Implemented and tested | Actual index 0 frame capture/release and bounded five-frame YOLO worker run; mocked stop/disconnect tests. Other cameras, live conveyor damage and long sessions are not verified. |
| Browser camera start/stop workflow | Implemented and tested | Fixed source-watcher configuration; two actual browser sessions persisted 194 and 267 frames without errors. Start/stop and live preview verified; health remained 200 after stop. Long-running industrial operation remains untested. |
| SQLite history/filtering/idempotence and error records | Implemented and tested | Temporary-database tests and persistent real smoke records; reruns do not trigger inspection buttons. |
| Candidate alerts and temporal matching | Implemented and tested | Consecutive-hit, expiry, reappearance and repeat suppression tests; real video candidate events and saved frames. No confirmed physical-defect identity claim. |
| Model performance interface and evaluation | Implemented and tested | Actual validation JSON, PR curves, confusion matrices, threshold analysis, per-image GT/prediction comparisons. |
| Model comparison/selection | Implemented and tested | Four checkpoints evaluated at 640 and 960 on identical validation data/GPU. Hash/condition/test-split checks and configured-confidence FP/FN guard tested. Baseline deliberately retained. |
| Dataset audit | Implemented and tested | Full actual dataset audit plus invalid-label, normal-label, orphan and leakage fixtures. Audit intentionally reports failure for current leakage. |
| Derived dataset | Implemented and tested | Verified_v2 has 112 train / 31 val / 19 test images; all 627 boxes and test entries retained. No exact duplicates/leakage. 333 source image/label/YAML hashes plus original checkpoint hashes verified unchanged. |
| Configurable training | Implemented and tested | Completed 100 GPU epochs in 691 seconds. Unique checkpoints, provenance, progress/failure reports and resolved native YAML. One pre-epoch path-resolution failure was fixed and preserved. |
| Retraining/promotion | Implemented and tested | New best.pt and last.pt preserved. New last.pt has higher mAP but 45 rather than 40 FP at .25 with identical TP/FN, so original best.pt remains the default. Further training awaits semantic annotation review rather than more blind experiments. |
| CPU benchmark and memory snapshots | Implemented and tested | Eight warm image repeats: median 24.9 ms; first inference ~2162 ms; RSS ~216 to ~448 MiB (not peak). |
| GPU inference/benchmark | Implemented and tested | User-approved .venv-conveyx-gpu has torch 2.12.0+cu130. Actual CUDA kernel and real-image CPU/GPU benchmark passed; GPU image/video/database and 115-frame camera smoke passed. Original CPU environment unchanged. |
| Automated tests | Implemented and tested | 51 passed in original CPU environment and 51 passed in CUDA environment; 0 failures/errors/skips. Two final dashboard regressions also pass. One upstream pandas warning per run. TEST_REPORT.md and outputs/reports/tests_cpu.xml/tests_gpu.xml. |
| Requirements, README, Windows launcher | Implemented and tested | requirements.txt plus direct verified version snapshot; original README retained; server/entry point launched. |
| Raspberry Pi / industrial cameras / PLC/motor integration | Not implemented | Frame-based extension interfaces provided. Deployment and hardware safety validation remain future work. |

## Fixes and remaining limitations

- Reused the original trained detection checkpoint, dataset layout, class convention and Ultralytics train/evaluate approach. Legacy scripts are preserved; use new `python -m src...` entry points to avoid hardcoded paths and test tuning.
- Added explicit overlap suppression even for YOLO26 end-to-end predictions. Counts remain candidate regions, not unique confirmed defects. Camera/video summaries use 0/1 presence; event/frame logs retain detail. Overview discloses that event records and summaries overlap.
- Isolated Streamlit dependencies in outputs/runtime rather than altering installed Python packages or replacing .venv. Current dashboard process dependencies can conflict with unrelated Google protobuf consumers; use a separate environment for those apps.
- Fixed SQLite placeholder errors uncovered by real smoke inference. Final database/alert tests pass. Failed attempts left their uniquely named media outputs intact; no originals were removed.
- Browser verification uncovered Streamlit magic rendering returned helper objects; explicit if statements fix that. Source watching is disabled after a native Python/Windows watcher crash. The fixed dashboard runs on 8502; a crashed test process retained 8501. Restart after source edits; alternate ports are configurable.
- Real camera frames were not saved as a demo unless candidate detection required evidence. Worker logs/session records are actual observations, not manufactured operating statistics.
- A final-run Windows TEMP ownership conflict caused 18 fixture setup errors in an intermediate run. Tests now use a fresh workspace-local temporary root, create its parent explicitly and disable shared pytest cache. The final run passes all 33 tests; the earlier permission report is retained under outputs/reports/tests_temp_permissions.xml.
- Remaining quality limits: weak baseline recall/localization, small dataset, duplicated split content and historical test reuse. Video browser codec support, long jobs, multi-user camera ownership and industrial operation are not production-qualified.

## Next decisions

1. Review broad/nested annotations and physical-damage semantics using ANNOTATION_REVIEW.md; do not automatically edit labels from model predictions.
2. Acquire real belt-motion videos and genuinely unseen test images before judging reliability or hardware readiness. Exact deduplication does not rule out scene-level similarity.
3. Industrial camera SDKs, Raspberry Pi deployment and physical control remain separate future integrations; no motor/PLC control is implemented.
