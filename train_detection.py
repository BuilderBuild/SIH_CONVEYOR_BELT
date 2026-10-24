
from ultralytics import YOLO
import torch

def main():
    print("CUDA available:", torch.cuda.is_available())

    if torch.cuda.is_available():
        print("GPU:", torch.cuda.get_device_name(0))

    model = YOLO("yolo26n.pt")

    results = model.train(
        data=r"D:\Conveyor_dataset\dataset_detection\data.yaml",
        epochs=100,
        imgsz=640,
        batch=8,
        patience=20,
        workers=0,
        device=0 if torch.cuda.is_available() else "cpu",
        project=r"D:\Conveyor_dataset\runs\detect",
        name="conveyor_defect_v1",
        exist_ok=False,
        plots=True,
        seed=42
    )

    print("\nTraining finished.")
    print("Best model: D:\\Conveyor_dataset\\runs\\detect\\conveyor_defect_v1\\weights\\best.pt")
    print("Last model: D:\\Conveyor_dataset\\runs\\detect\\conveyor_defect_v1\\weights\\last.pt")

if __name__ == "__main__":
    main()
