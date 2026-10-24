# ConveyX ML continuation report

Verified 24 October 2026. The GPU dashboard is available at http://127.0.0.1:8502; launch with `./launch-gpu.ps1` from PowerShell.

## Completed work

- Created the separately approved CUDA environment, without replacing the original CPU torch installation.
- Created and audited a separate exact-deduplicated dataset. All retained files stay in their original split; all test entries and all 627 defect boxes are preserved.
- Completed one 100-epoch GPU training experiment in a unique output directory.
- Compared four checkpoint files at both 640 and 960 on matching validation data/GPU.
- Retained the original best.pt after reviewing the configured-threshold FP/FN tradeoff.
- Ran one final held-out evaluation after selection; no tuning followed it.
- Verified GPU image/video inference, SQLite storage/retrieval and actual camera capture/release.
- Passed all 51 tests in both the original CPU environment and the approved CUDA environment.

## Dataset and preservation

| Split | Images | Boxes | Empty labels |
|---|---:|---:|---:|
| train | 112 | 453 | 57 |
| val | 31 | 116 | 16 |
| test | 19 | 58 | 10 |

Audit valid: True; exact duplicates: 0; cross-split exact leakage groups: 0.
Source files checked: 333; originals unchanged: True; original checkpoints unchanged: True.

Source originals remain under dataset_detection and CVAT_DETECTED_YOLO. Derived metadata and exclusion manifest: dataset_detection_verified_v2/manifest.json. Exact deduplication does not establish scene independence or semantic annotation quality.

## Training

Experiment: `conveyx_20261024T025608_1e622a05`; epochs: 100; elapsed seconds: 691.4.
Best checkpoint: `D:\Conveyor_dataset\runs\detect\conveyx_20261024T025608_1e622a05\weights\best.pt`.
Final checkpoint: `D:\Conveyor_dataset\runs\detect\conveyx_20261024T025608_1e622a05\weights\last.pt`.
Parameters: pretrained yolo26n.pt, 960 pixels, batch 8, CUDA device 0, patience 20, seed 42, workers 0. The original annotations were not changed.
An initial attempt failed before epoch 1 because native Ultralytics resolved relative YAML path differently. The trainer now writes an explicit resolved runtime YAML; the completed run succeeded. Progress count is reconciled to actual results.csv rows so final validation callbacks cannot report epoch 101 for a 100-epoch run.

## Matched validation results

| Checkpoint | Size | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|---:|
| conveyor_defect_v1/best.pt | 640 | 0.33939 | 0.40517 | 0.26843 | 0.09474 |
| conveyor_defect_v1/last.pt | 640 | 0.36112 | 0.31675 | 0.24816 | 0.08230 |
| conveyx_20261024T025608_1e622a05/best.pt | 640 | 0.29044 | 0.34483 | 0.25478 | 0.09183 |
| conveyx_20261024T025608_1e622a05/last.pt | 640 | 0.36500 | 0.29310 | 0.29320 | 0.10327 |
| conveyor_defect_v1/best.pt | 960 | 0.32225 | 0.31897 | 0.22384 | 0.07184 |
| conveyor_defect_v1/last.pt | 960 | 0.28470 | 0.33621 | 0.21369 | 0.06279 |
| conveyx_20261024T025608_1e622a05/best.pt | 960 | 0.31042 | 0.31897 | 0.21224 | 0.07795 |
| conveyx_20261024T025608_1e622a05/last.pt | 960 | 0.45231 | 0.27586 | 0.24167 | 0.07719 |

Native precision/recall are reported at the library-selected operating point. The deployment decision also checks the actual configured confidence below. Reports use the same 31-image validation split; no test reports enter selection.

## Deployment decision

Retained `D:\Conveyor_dataset\runs\detect\conveyor_defect_v1\weights\best.pt` at 640 pixels, confidence 0.25 and IoU .45.

| At actual confidence | TP | Unmatched predictions (FP) | Unmatched GT boxes (FN) |
|---|---:|---:|---:|
| Original baseline | 32 | 40 | 84 |
| mAP-ranked new candidate | 32 | 45 | 84 |

The new last.pt has a modest higher mAP, but it adds unmatched predictions without reducing missed boxes at .25. The original baseline remains the operational default. All new checkpoints and reports are preserved. Box matches are not counts of unique physical defects.

## Final held-out evaluation

Preserved test split: 19 images / 58 GT boxes. {'precision': 0.3870701901750546, 'recall': 0.3920278691470483, 'mAP50': 0.29869244464443984, 'mAP50_95': 0.1078003125020254}
The selection decision was already recorded before this final test run. Historical test reuse means this is not a new independent acceptance set.

## CUDA benchmark and smoke

GPU: NVIDIA GeForce RTX 5050 Laptop GPU; torch: 2.12.0+cu130; CUDA build: 13.0; actual CUDA kernel verified: True.
Synchronized warm median full calls on one real image: CPU 41.98 ms, GPU 24.43 ms. Not guaranteed camera FPS.
GPU image/SQLite roundtrip: True; video frames: 12; annotated video decoded: True.
Actual camera 0: 115 frames, state stopped, worker stopped True, error ''. Last measured processing FPS 35.9; smoke scene only.

## Remaining work requiring new evidence

- Human review of broad/nested annotation boxes and physical-damage semantics: ANNOTATION_REVIEW.md.
- Real moving-conveyor videos, long-duration runs and genuinely unseen test acquisitions.
- Industrial camera/Raspberry Pi integration and any future separately validated hardware safety design.

There is no automatic motor/PLC control and no guarantee that a no-detection result means a healthy belt.
