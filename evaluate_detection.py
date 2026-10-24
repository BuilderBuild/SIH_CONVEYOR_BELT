
from ultralytics import YOLO

model_path = (
    r"D:\Conveyor_dataset\runs\detect"
    r"\conveyor_defect_v1\weights\best.pt"
)
data_path = r"D:\Conveyor_dataset\dataset_detection\data.yaml"

model = YOLO(model_path)

print("\n=== Evaluating on the held-out TEST split ===")

metrics = model.val(
    data=data_path,
    split="test",
    imgsz=640,
    workers=0,
    plots=True
)

print("\nTest evaluation finished.")
print("Precision:", metrics.box.mp)
print("Recall:", metrics.box.mr)
print("mAP50:", metrics.box.map50)
print("mAP50-95:", metrics.box.map)

print("\n=== Saving predictions on test images ===")

results = model.predict(
    source=r"D:\Conveyor_dataset\dataset_detection\images\test",
    imgsz=640,
    conf=0.15,
    save=True,
    project=r"D:\Conveyor_dataset\runs\detect",
    name="conveyor_test_predictions",
    exist_ok=False
)

print("\nPredictions saved.")
