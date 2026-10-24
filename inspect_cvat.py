
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

def find_folder(prefix):
    matches = [
        p for p in ROOT.iterdir()
        if p.is_dir() and p.name.startswith(prefix)
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one folder starting with {prefix!r}; "
            f"found: {[p.name for p in matches]}"
        )
    return matches[0]

def inspect_export(prefix, original_class):
    export = find_folder(prefix)
    labels_dir = export / "labels"
    train_file = export / "train.txt"
    original_dir = ROOT / "Images" / original_class

    print(f"\n{'=' * 55}")
    print("Export:", export.name)
    print("Original images:", original_dir)
    print("Labels folder exists:", labels_dir.is_dir())
    print("train.txt exists:", train_file.is_file())

    if not labels_dir.is_dir() or not train_file.is_file():
        print("Cannot inspect this export fully.")
        return

    label_files = list(labels_dir.glob("*.txt"))
    original_images = [
        p for p in original_dir.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    ]

    listed_paths = [
        line.strip()
        for line in train_file.read_text(
            encoding="utf-8-sig"
        ).splitlines()
        if line.strip()
    ]

    print("Paths in train.txt:", len(listed_paths))
    print("Label files:", len(label_files))
    print("Original images:", len(original_images))

    label_stems = {p.stem for p in label_files}
    image_by_stem = {}
    for p in original_images:
        image_by_stem.setdefault(p.stem, []).append(p)

    print("First 5 listed paths:")
    for path in listed_paths[:5]:
        print(" ", path)

    print("First 10 label files:")
    for p in sorted(label_files)[:10]:
        print(" ", p.name)

    print("\nMatching examples:")
    for p in sorted(label_files)[:10]:
        matches = image_by_stem.get(p.stem, [])
        print(
            f"  {p.name} -> "
            + (", ".join(x.name for x in matches)
               if matches else "NO ORIGINAL IMAGE MATCH")
        )

    listed_stems = {
        Path(path.replace("\\", "/")).stem
        for path in listed_paths
    }

    print("\nListed image stems with labels:",
          len(listed_stems & label_stems))
    print("Listed image stems without labels:",
          len(listed_stems - label_stems))
    print("Label stems absent from train.txt:",
          len(label_stems - listed_stems))

inspect_export("CVAT_DETECTED", "defected")
inspect_export("CVAT_NORMAL", "normal")
