import json
import base64
import uuid
from kafka import KafkaProducer

# ----------------------------------
# Kafka Producer setup
# ----------------------------------
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

# ----------------------------------
# Helper: image → base64
# ----------------------------------
def image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# ----------------------------------
# Send image to Kafka
# ----------------------------------
def send_image(image_path: str):
    message = {
        "frame_id": str(uuid.uuid4()),
        "image_base64": image_to_base64(image_path)
    }

    producer.send("raw_frames", value=message)
    producer.flush()

    print(f"✅ Sent image to Kafka: {image_path}")

# ----------------------------------
# Entry point
# ----------------------------------
if __name__ == "__main__":
    # 🔁 CHANGE THIS PATH TO ANY TEST IMAGE
    IMAGE_PATH = "test.jpg"

    send_image(IMAGE_PATH)
