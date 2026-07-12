from prometheus_client import Counter, Histogram, Gauge

# API Request Counter
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint"]
)

# API Response Time
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP Request Duration",
    ["method", "endpoint"]
)

# Runtime CPU Usage
CPU_USAGE = Gauge(
    "cpu_usage_percent",
    "Current CPU Usage"
)

# Runtime Memory Usage
MEMORY_USAGE = Gauge(
    "memory_usage_percent",
    "Current Memory Usage"
)

# Deployment Counter
DEPLOYMENT_COUNT = Counter(
    "deployment_created_total",
    "Total Deployments Created"
)

# Prediction Counter
PREDICTION_COUNT = Counter(
    "prediction_requests_total",
    "Total Prediction Requests"
)