import cv2
import time
from ultralytics import YOLO

MODEL_PATH = "models/best.pt"

def main():
    print("Starting edge camera inference...")
    model = YOLO(MODEL_PATH)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open USB camera")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        start = time.time()
        results = model(frame)
        latency = time.time() - start

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
                cv2.putText(
                    frame,
                    f"{conf:.2f}",
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0,255,0),
                    1
                )

        cv2.putText(
            frame,
            f"Inference: {latency*1000:.1f} ms",
            (10,30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0,255,0),
            2
        )

        cv2.imshow("Crack Detection (Edge)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
