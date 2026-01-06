import json
from kafka import KafkaProducer

# Lazy-initialized producer (IMPORTANT)
_producer = None


def get_producer():
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers="localhost:9092",
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
    return _producer


def send_detection(message: dict):
    producer = get_producer()
    producer.send("detections", value=message)
    producer.flush()
