
from pathlib import Path
from shutil import copy2
import random

# Original images and new dataset
SOURCE = Path("Images")
DEST = Path("dataset")

CLASSES = ["defected", "normal"]
EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# Reproducible 70/20/10 split
random.seed(42)
SPLITS = {
    "train": 0.70,
    "val": 0.20,
    "test": 0.10,
}

# Safety checks
if not SOURCE.exists():
    raise FileNotFoundError(
        f"Cannot find {SOURCE.resolve()}. "
        "Run this script from your Conveyor folder."
    )

if DEST.exists():
    raise FileExistsError(
        f"{DEST.resolve()} already exists. "
        "Rename or back it up before preparing a fresh dataset."
    )

# Validate and collect image files
files_by_class = {}

for class_name in CLASSES:
    folder = SOURCE / class_name

    if not folder.is_dir():
        raise FileNotFoundError(
            f"Missing class folder: {folder.resolve()}"
        )

    files = sorted(
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in EXTENSIONS
    )

    if len(files) < 3:
        raise ValueError(
            f"Class '{class_name}' has only {len(files)} images. "
            "At least 3 are needed for this basic split."
        )

    random.shuffle(files)
    files_by_class[class_name] = files

# Copy each class into train, validation and test
for class_name, files in files_by_class.items():
    n = len(files)
    n_train = int(n * 0.70)
    n_val = int(n * 0.20)

    # Ensure every split gets at least one image
    if n_train == 0 or n_val == 0 or n_train + n_val >= n:
        raise ValueError(
            f"Not enough images in '{class_name}' for a 70/20/10 split."
        )

    assignments = {
        "train": files[:n_train],
        "val": files[n_train:n_train + n_val],
        "test": files[n_train + n_val:],
    }

    for split, split_files in assignments.items():
        target = DEST / split / class_name
        target.mkdir(parents=True, exist_ok=True)

        for image_path in split_files:
            copy2(image_path, target / image_path.name)

# Report dataset counts
print("\nDataset prepared successfully:\n")

for split in SPLITS:
    print(f"{split.upper()}:")
    for class_name in CLASSES:
        count = len(list(
            (DEST / split / class_name).iterdir()
        ))
        print(f"  {class_name}: {count}")

print(f"\nDataset location: {DEST.resolve()}")
print("Original images were not modified.")
