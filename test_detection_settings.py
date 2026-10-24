
from ultralytics import YOLO

model_path = (
    r"D:\Conveyor_dataset\runs\detect"
    r"\conveyor_defect_v1\weights\best.pt"
)

model = YOLO(model_path)

source = r"D:\Conveyor_dataset\dataset_detection\images\test"

results = model.predict(
    source=source,
    imgsz=640,

    # Ignore low-confidence predictions
    conf=0.25,

    # More aggressive suppression of overlapping boxes
    iou=0.45,

    # Limit excessive detections in one image
    max_det=20,

    save=True,
    project=r"D:\Conveyor_dataset\runs\detect",
    name="conveyor_test_tuned",
    exist_ok=False
)

print("Finished.")
print(
    r"Open D:\Conveyor_dataset\runs\detect"
    r"\conveyor_test_tuned"
)
