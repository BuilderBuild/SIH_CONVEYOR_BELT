
from pathlib import Path
import random
import cv2

ROOT = Path(r"D:\Conveyor_dataset\dataset_detection")
SPLIT = "train"

image_dir = ROOT / "images" / SPLIT
label_dir = ROOT / "labels" / SPLIT
output_dir = ROOT / "box_preview"
output_dir.mkdir(exist_ok=True)

images = [
    p for p in image_dir.iterdir()
    if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
]

def draw_boxes(image_path):
    image = cv2.imread(str(image_path))
    if image is None:
        print("Could not read:", image_path)
        return

    h, w = image.shape[:2]
    label_path = label_dir / f"{image_path.stem}.txt"

    if label_path.exists():
        for line in label_path.read_text().splitlines():
            values = line.split()
            if len(values) != 5:
                continue

            cls, xc, yc, bw, bh = map(float, values)
            x1 = int((xc - bw / 2) * w)
            y1 = int((yc - bh / 2) * h)
            x2 = int((xc + bw / 2) * w)
            y2 = int((yc + bh / 2) * h)

            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                image, "DEFECT",
                (max(0, x1), max(20, y1 - 5)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
            )

    output_path = output_dir / image_path.name
    cv2.imwrite(str(output_path), image)
    print(output_path)

random.seed(42)
for path in random.sample(images, min(10, len(images))):
    draw_boxes(path)

print(f"\nPreview images saved in: {output_dir}")
