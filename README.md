

# Airport Runway & Road Crack Detection System

Overview

This project is a production-grade computer vision system designed to detect cracks on airport runways and roads. It uses a YOLOv8 object detection model and is built with a clear separation between training, inference, monitoring, and deployment.

The system is designed with real-world constraints in mind, including observability, fault tolerance, and edge deployment on resource-constrained devices such as Raspberry Pi 5.



Problem Statement

Manual inspection of runways and roads is slow, error-prone, and expensive. This project automates crack detection using computer vision, enabling faster inspections, consistent results, and easier integration with downstream systems.



High-Level Architecture

The system is divided into four logical layers:

* Training (offline)
* Inference service (online)
* Messaging and monitoring
* Edge deployment


                ┌──────────────┐
                │   Dataset    │
                └──────┬───────┘
                       │
                 (Offline Training)
                       │
                ┌──────▼───────┐
                │ YOLOv8 Model │
                └──────┬───────┘
                       │
               ┌───────▼────────┐
               │ Inference API  │
               │   (FastAPI)    │
               └───────┬────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   REST API        Kafka Consumer   Prometheus
        │              │              │
        ▼              ▼              ▼
     Clients     Async Inference   Metrics & Alerts




## Project Flow (Simple Explanation)

1. Model Training (Offline)

* Crack images are collected and cleaned.
* A YOLOv8 model is trained locally using GPU.
* The trained model is exported as `.pt` or `.onnx`.
* Training artifacts are not part of runtime deployment.

This keeps inference lightweight and reproducible.



2. Inference Service (FastAPI)

The inference service is a FastAPI application that:

* Loads the trained YOLO model once at startup.
* Exposes REST endpoints:

  * `/health` – service health check
  * `/infer` – image-based crack detection
  * `/metrics` – Prometheus metrics


Client Image
     │
     ▼
┌─────────────┐
│  FastAPI    │
│  /infer     │
└──────┬──────┘
       │
┌──────▼──────┐
│ YOLO Model  │
└──────┬──────┘
       │
   Detection Results


3. Kafka-Based Asynchronous Inference

To support event-driven pipelines, Kafka is used.

* Producers send image frames or metadata to a Kafka topic.
* The inference service runs a background Kafka consumer.
* Incoming messages are processed using the same YOLO model.
* Detection results are published to another Kafka topic.


Kafka Topic: raw_frames
        │
        ▼
┌──────────────────┐
│ Kafka Consumer   │
│ (Inference App)  │
└───────┬──────────┘
        │
   YOLO Inference
        │
        ▼
Kafka Topic: detections


This decouples image ingestion from inference and allows easy scaling.



4. Monitoring and Observability

The inference service exposes Prometheus metrics such as:

* Total inference requests
* Inference latency
* Error count

Prometheus scrapes these metrics, and Grafana visualizes them using dashboards.


Inference Service
       │
   /metrics
       │
┌──────▼──────┐
│ Prometheus  │
└──────┬──────┘
       │
┌──────▼──────┐
│  Grafana    │
└─────────────┘


This provides real-time visibility into system health and performance.



Edge Deployment (Raspberry Pi 5)

The system is designed for edge deployment:

* Raspberry Pi 5 running Ubuntu
* USB webcam as image source
* OpenCV for frame capture
* YOLO inference runs locally on CPU
* FastAPI runs as a background service using `systemd`

Heavy components such as Kafka brokers, Prometheus, and Grafana run off-device (laptop or server), keeping the edge device stable and efficient.


USB Camera
     │
     ▼
 OpenCV Capture
     │
     ▼
 YOLO Inference (Pi)
     │
     ├── Local display / alerts
     └── Kafka / API (optional)




Repository Structure


road_crack_detection/
├── inference_service/
│   ├── app/
│   ├── models/
│   └── requirement.txt
│
├── monitoring/
│   └── prometheus.yml
│
├── kafka/
│   ├── docker-compose.yml
│   └── producer.py
│
├── README.md
└── .gitignore


---

Key Design Decisions

* Strict separation of training and inference
* Event-driven architecture using Kafka
* Built-in monitoring from day one
* Edge-first design with minimal dependencies
* Clean Git hygiene with allow-listed tracking



 Future Enhancements

* Model optimization for edge deployment (quantization)
* Video stream ingestion instead of single frames
* Automated data drift detection
* Cloud-based alerting
* CI/CD pipeline for inference service

## Raspberry Pi 5 Edge Deployment

This project supports edge deployment on Raspberry Pi 5 running Ubuntu.

Hardware
- Raspberry Pi 5
- USB webcam

Software
- Ubuntu Server 22.04
- Python 3.10+
- CPU-only YOLO inference

Steps
1. Clone the repository on Raspberry Pi
2. Create a virtual environment
3. Install dependencies
4. Run `edge_camera.py` for live inference
5. Optionally enable systemd service for auto-start

Kafka, Prometheus, and Grafana are intended to run off-device.