from prometheus_client import Counter, Histogram

# Total inference requests
INFERENCE_REQUESTS = Counter(
    "inference_requests_total",
    "Total number of inference requests"
)

# Inference latency
INFERENCE_LATENCY = Histogram(
    "inference_latency_seconds",
    "Time taken for inference"
)

# Inference errors
INFERENCE_ERRORS = Counter(
    "inference_errors_total",
    "Total number of inference errors"
)
