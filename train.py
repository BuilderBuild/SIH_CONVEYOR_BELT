
from pathlib import Path
from ultralytics import YOLO

DATASET = Path("dataset")

# Verify that the dataset was prepared
for split in ["train", "val", "test"]:
    for class_name in ["defected", "normal"]:
        folder = DATASET / split / class_name

        if not folder.is_dir():
            raise FileNotFoundError(
                f"Missing folder: {folder.resolve()}"
            )

        image_count = sum(
            1 for p in folder.iterdir()
            if p.is_file()
            and p.suffix.lower() in {
                ".jpg", ".jpeg", ".png", ".bmp", ".webp"
            }
        )

        if image_count == 0:
            raise ValueError(f"No images found in {folder}")

# Load pretrained classification model
model = YOLO("yolo26n-cls.pt")

# Train the model
model.train(
    data=str(DATASET.resolve()),
    epochs=50,
    imgsz=224,
    batch=8,
    patience=10,
    seed=42,
    workers=0,
    project="runs/classify",
    name="conveyor_health"
)

print("\nTraining finished.")
print("Best model should be saved in:")
print("runs/classify/conveyor_health/weights/best.pt")
