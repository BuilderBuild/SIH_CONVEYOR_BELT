
from pathlib import Path
from shutil import copy2

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "dataset"
DEST = ROOT / "dataset_detection"

SPLITS = ["train", "val", "test"]
CLASSES = ["defected", "normal"]
EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

if not SOURCE.is_dir():
    raise FileNotFoundError(
        f"Classification dataset not found: {SOURCE}"
    )

if DEST.exists():
    raise FileExistsError(
        f"{DEST} already exists. Back it up or rename it "
        "before creating a fresh detection dataset."
    )

for split in SPLITS:
    for class_name in CLASSES:
        source_folder = SOURCE / split / class_name

        if not source_folder.is_dir():
            raise FileNotFoundError(
                f"Missing folder: {source_folder}"
            )

        for image in source_folder.iterdir():
            if not image.is_file():
                continue

            if image.suffix.lower() not in EXTENSIONS:
                continue

            target_folder = DEST / "images" / split
            target_folder.mkdir(parents=True, exist_ok=True)

            # Prefix with class to avoid duplicate filenames
            # such as defected/1.jpeg and normal/1.jpeg.
            target_name = f"{class_name}_{image.name}"
            copy2(image, target_folder / target_name)

        (DEST / "labels" / split).mkdir(
            parents=True, exist_ok=True
        )

print(f"Detection folders created at: {DEST}")
print("Images copied. Bounding boxes still need annotation.")
