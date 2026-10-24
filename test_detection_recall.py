
from ultralytics import YOLO

model = YOLO(
    r"D:\Conveyor_dataset\runs\detect\conveyor_defect_v1\weights\best.pt"
)

model.predict(
    source=r"D:\Conveyor_dataset\dataset_detection\images\test",
    imgsz=640,
    conf=0.15,
    iou=0.60,
    max_det=100,
    save=True,
    project=r"D:\Conveyor_dataset\runs\detect",
    name="conveyor_test_recall",
    exist_ok=False
)

print("Predictions saved in conveyor_test_recall")
