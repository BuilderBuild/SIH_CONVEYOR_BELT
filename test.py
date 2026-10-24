
# from ultralytics import YOLO

# MODEL_PATH = (
#     "runs/classify/runs/classify/conveyor_health-2/weights/best.pt"
# )

# model = YOLO(MODEL_PATH)

# # Evaluate on the separate test split
# metrics = model.val(
#     data="dataset",
#     split="test",
#     imgsz=224,
#     workers=0
# )

# print("\nTest evaluation complete.")
# print(metrics)




from ultralytics import YOLO

model = YOLO(
    "runs/classify/runs/classify/conveyor_health-2/weights/best.pt"
)

metrics = model.val(
    data="dataset",
    split="test",
    imgsz=224,
    workers=0,
    plots=True
)

print("\nTest evaluation finished.")
print(metrics)
