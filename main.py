from ultralytics import YOLO
import torch, os

def main():
    # --- CUDA Check ---
    print("CUDA available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("Using GPU:", torch.cuda.get_device_name(0))
    else:
        print("⚠️ Training on CPU (will be slower)")

    # --- Paths ---
    project_dir = r"C:\Users\Admin\Desktop\road_crack_detection"
    data_yaml = os.path.join(project_dir, "filtered_4classes_ready", "data.yaml")
    model_path = os.path.join(project_dir, "yolov8m.pt")

    # --- Load Model ---
    model = YOLO(model_path)   # YOLOv8m backbone

    # --- Training ---
    results = model.train(
        data=data_yaml,
        epochs=70,
        imgsz=640,
        batch=8,             # safe for 16 GB GPU
        device=0,            # GPU 0
        workers=8,
        half=True,           # use mixed precision (saves ~40% VRAM)
        cache="disk",        # avoid OOM from RAM caching
        lr0=0.001,
        patience=10,         # early stopping
        project=os.path.join(project_dir, "runs"),
        name="finetune_yolov8m_4class",
        pretrained=True,
        verbose=True
    )

    print(f"✅ Training complete! Best weights saved at: {results.save_dir}")

if __name__ == "__main__":
    main()
