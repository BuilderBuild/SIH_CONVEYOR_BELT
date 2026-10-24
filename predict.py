
from pathlib import Path
from ultralytics import YOLO

model = YOLO(
    "runs/classify/runs/classify/conveyor_health-2/weights/best.pt"
)

image_path = Path("Images/defected")

# Select one image automatically
images = [
    p for p in image_path.iterdir()
    if p.suffix.lower() in {
        ".jpg", ".jpeg"
    }
]

if not images:
    raise FileNotFoundError(
        f"No images found in {image_path}"
    )

results = model.predict(
    source=str(images[0]),
    imgsz=224
)

for result in results:
    prediction = result.probs
    class_name = result.names[prediction.top1]
    confidence = float(prediction.top1conf)

    print("Image:", images[0].name)
    print("Prediction:", class_name)
    print(f"Confidence: {confidence:.2%}")
