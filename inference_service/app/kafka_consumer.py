import json
import base64
import cv2
import numpy as np
import time
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

from app.kafka_producer import send_detection
from app.metrics import (
    INFERENCE_REQUESTS,
    INFERENCE_LATENCY,
    INFERENCE_ERRORS
)

# -----------------------------
# Safe JSON deserializer
# -----------------------------
def safe_json_deserializer(v):
    try:
        return json.loads(v.decode("utf-8"))
    except Exception:
        return None


# -----------------------------
# Kafka Consumer with RETRY
# -----------------------------
def start_kafka_consumer(model):
    print("🟡 Kafka consumer thread started")

    while True:
        try:
            print("🔄 Attempting to connect to Kafka...")

            consumer = KafkaConsumer(
                "raw_frames",
                bootstrap_servers="localhost:9092",
                value_deserializer=safe_json_deserializer,
                auto_offset_reset="latest",
                enable_auto_commit=True,
                group_id="inference-group",
            )

            print("🔥 Kafka consumer connected successfully")

            for message in consumer:
                payload = message.value

                if payload is None:
                    continue

                INFERENCE_REQUESTS.inc()
                start_time = time.time()

                try:
                    img_bytes = base64.b64decode(payload["image_base64"])
                    np_img = np.frombuffer(img_bytes, np.uint8)
                    image = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

                    if image is None:
                        raise ValueError("Invalid image frame")

                    results = model(image)

                    detections = []
                    for r in results:
                        for box in r.boxes:
                            detections.append({
                                "class_id": int(box.cls[0]),
                                "confidence": float(box.conf[0]),
                                "bbox_xyxy": box.xyxy[0].tolist()
                            })

                    INFERENCE_LATENCY.observe(time.time() - start_time)

                    send_detection({
                        "frame_id": payload.get("frame_id"),
                        "detections": detections
                    })

                except Exception as e:
                    INFERENCE_ERRORS.inc()
                    print("❌ Inference error:", e)

        except NoBrokersAvailable:
            print("⏳ Kafka not available yet. Retrying in 5 seconds...")
            time.sleep(5)

        except Exception as e:
            print("❌ Kafka consumer fatal error:", e)
            time.sleep(5)
