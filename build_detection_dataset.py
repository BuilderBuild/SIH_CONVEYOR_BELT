
from pathlib import Path
from shutil import copy2
import random
import re

ROOT = Path(__file__).resolve().parent

DEFECT_IMAGES = ROOT / "Images" / "defected"
NORMAL_IMAGES = ROOT / "Images" / "normal"
LABELS = ROOT / "CVAT_DETECTED_YOLO" / "labels" / "train"
CLASS_DATASET = ROOT / "dataset"
DEST = ROOT / "dataset_detection"

EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
SPLITS = ["train", "val", "test"]
random.seed(42)


def image_files(folder):
    return [
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in EXTS
    ]


def validate_label(label_path):
    lines = [
        line.strip()
        for line in label_path.read_text(
            encoding="utf-8-sig"
        ).splitlines()
        if line.strip()
    ]

    if not lines:
        raise ValueError(
            f"Defect annotation is empty: {label_path}"
        )

    for line_no, line in enumerate(lines, start=1):
        parts = line.split()

        if len(parts) != 5:
            raise ValueError(
                f"{label_path}, line {line_no}: "
                "expected 5 values per bounding box."
            )

        try:
            cls = int(parts[0])
            coords = [float(v) for v in parts[1:]]
        except ValueError:
            raise ValueError(
                f"Invalid numeric values in {label_path}, "
                f"line {line_no}"
            )

        if cls != 0:
            raise ValueError(
                f"Unexpected class ID {cls} in {label_path}"
            )

        x, y, w, h = coords

        if not all(0 <= v <= 1 for v in coords):
            raise ValueError(
                f"Coordinates outside [0,1] in {label_path}"
            )

        if w <= 0 or h <= 0:
            raise ValueError(
                f"Zero/negative box size in {label_path}"
            )

        if x - w / 2 < -1e-6 or x + w / 2 > 1 + 1e-6:
            raise ValueError(
                f"Box exceeds image width in {label_path}"
            )

        if y - h / 2 < -1e-6 or y + h / 2 > 1 + 1e-6:
            raise ValueError(
                f"Box exceeds image height in {label_path}"
            )

    return len(lines)


# Check inputs
for folder in [DEFECT_IMAGES, NORMAL_IMAGES, LABELS]:
    if not folder.is_dir():
        raise FileNotFoundError(f"Missing folder: {folder}")

if not CLASS_DATASET.is_dir():
    raise FileNotFoundError(
        "Missing dataset/train, dataset/val and dataset/test. "
        "Prepare your existing classification split first."
    )

if DEST.exists():
    raise FileExistsError(
        f"{DEST} already exists. Rename/back it up before "
        "building a fresh dataset."
    )

# Match defective images and annotations by numeric stem.
defect_by_stem = {p.stem: p for p in image_files(DEFECT_IMAGES)}
label_by_stem = {
    p.stem: p for p in LABELS.glob("*.txt")
}

if len(defect_by_stem) != len(image_files(DEFECT_IMAGES)):
    raise ValueError("Duplicate defective image stems found.")

if set(label_by_stem) != set(defect_by_stem):
    print("Image stems missing labels:",
          sorted(set(defect_by_stem) - set(label_by_stem)))
    print("Labels missing images:",
          sorted(set(label_by_stem) - set(defect_by_stem)))
    raise ValueError("Image/annotation matching is incomplete.")

# Read the existing classification split to preserve its assignment.
split_by_key = {}

for split in SPLITS:
    for cls, folder_name in [
        ("defected", "defected"),
        ("normal", "normal")
    ]:
        folder = CLASS_DATASET / split / folder_name

        if not folder.is_dir():
            raise FileNotFoundError(f"Missing split folder: {folder}")

        for p in image_files(folder):
            key = (cls, p.name)
            if key in split_by_key:
                raise ValueError(f"Duplicate split entry: {key}")
            split_by_key[key] = split

# Map original image names to the existing split.
def split_for(cls, image):
    key = (cls, image.name)
    if key not in split_by_key:
        raise ValueError(
            f"{image.name} is not present in the existing "
            f"classification split for {cls}. Resolve this "
            "before assigning it to detection."
        )
    return split_by_key[key]


# Validate annotations before copying anything.
box_count = 0
for stem, label in label_by_stem.items():
    box_count += validate_label(label)

# Plan image copies.
plans = []

for stem, image in defect_by_stem.items():
    plans.append((
        split_for("defected", image),
        image,
        label_by_stem[stem]
    ))

for image in image_files(NORMAL_IMAGES):
    plans.append((
        split_for("normal", image),
        image,
        None
    ))

# Check no duplicate destination filenames.
seen = set()
for split, image, label in plans:
    target_name = f"{'defected' if label else 'normal'}_{image.name}"
    key = (split, target_name.lower())
    if key in seen:
        raise ValueError(f"Duplicate destination filename: {key}")
    seen.add(key)

# Create dataset and copy files.
for split in SPLITS:
    (DEST / "images" / split).mkdir(
        parents=True, exist_ok=True
    )
    (DEST / "labels" / split).mkdir(
        parents=True, exist_ok=True
    )

counts = {s: {"defected": 0, "normal": 0} for s in SPLITS}

for split, image, label in plans:
    cls = "defected" if label else "normal"
    target_name = f"{cls}_{image.name}"

    copy2(image, DEST / "images" / split / target_name)

    label_target = DEST / "labels" / split / (
        Path(target_name).stem + ".txt"
    )

    if label:
        copy2(label, label_target)
    else:
        # Empty labels represent normal images with no defects.
        label_target.write_text("", encoding="utf-8")

    counts[split][cls] += 1

yaml_text = f"""path: {DEST.as_posix()}
train: images/train
val: images/val
test: images/test

names:
  0: defect
"""

(DEST / "data.yaml").write_text(yaml_text, encoding="utf-8")

print("\nDataset created:", DEST)
print("Validated bounding boxes:", box_count)
print("\nSplit counts:")
for split in SPLITS:
    print(
        f"{split}: defected={counts[split]['defected']}, "
        f"normal={counts[split]['normal']}"
    )

print("\ndata.yaml created.")
print("Original photos and CVAT annotations were not modified.")
