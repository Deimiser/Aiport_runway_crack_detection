from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from ultralytics import YOLO
import cv2
import numpy as np
import timecd training
import os

# Prometheus imports
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.metrics import (
    INFERENCE_REQUESTS,
    INFERENCE_LATENCY,
    INFERENCE_ERRORS
)


# ----------------------------------
# FastAPI app initialization
# ----------------------------------
app = FastAPI(
    title="Runway Crack Detection - Inference Service",
    description="YOLOv8 inference service with Prometheus metrics",
    version="1.0.0"
)

# ----------------------------------
# Load YOLO model ONCE at startup
# ----------------------------------
MODEL_PATH = os.path.join("models", "best.pt")
model = YOLO(MODEL_PATH)

# ----------------------------------
# Health check endpoint
# ----------------------------------
@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": True
    }

# ----------------------------------
# 🔥 INFERENCE ENDPOINT (THIS IS THE infer FUNCTION)
# ----------------------------------
@app.post("/infer")
async def infer(file: UploadFile = File(...)):
    """
    Accepts an image file,
    runs YOLO inference,
    returns detected bounding boxes.
    """

    # Count request
    INFERENCE_REQUESTS.inc()

    start_time = time.time()

    try:
        # Read uploaded image
        contents = await file.read()
        np_img = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        if image is None:
            INFERENCE_ERRORS.inc()
            return {"error": "Invalid image file"}

        # Run YOLO inference
        results = model(image)

        detections = []
        for r in results:
            for box in r.boxes:
                detections.append({
                    "class_id": int(box.cls[0]),
                    "confidence": float(box.conf[0]),
                    "bbox_xyxy": box.xyxy[0].tolist()
                })

        # Record inference latency
        INFERENCE_LATENCY.observe(time.time() - start_time)

        return {
            "num_detections": len(detections),
            "detections": detections
        }

    except Exception as e:
        INFERENCE_ERRORS.inc()
        return {"error": str(e)}

# ----------------------------------
# Prometheus metrics endpoint
# ----------------------------------
@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
