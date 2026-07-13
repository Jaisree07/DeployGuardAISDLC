from prometheus_client import Counter, Histogram, Gauge

# =====================================================
# HTTP Metrics
# =====================================================

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP Request Duration",
    ["method", "endpoint"]
)

API_ERRORS = Counter(
    "http_errors_total",
    "Total HTTP Errors",
    ["method", "endpoint", "status_code"]
)

# =====================================================
# Runtime Metrics
# =====================================================

CPU_USAGE = Gauge(
    "deployguard_cpu_percent",
    "DeployGuard API CPU Usage (%)"
)

MEMORY_USAGE = Gauge(
    "deployguard_memory_mb",
    "DeployGuard API Memory Usage (MB)"
)

# =====================================================
# Deployment Metrics
# =====================================================

DEPLOYMENT_COUNT = Counter(
    "deployment_created_total",
    "Total Deployments Created"
)

DEPLOYMENT_SUCCESS = Counter(
    "deployment_success_total",
    "Successful Deployments"
)

DEPLOYMENT_FAILURE = Counter(
    "deployment_failure_total",
    "Failed Deployments"
)

ACTIVE_DEPLOYMENTS = Gauge(
    "active_deployments",
    "Currently Active Deployments"
)

# =====================================================
# ML Prediction Metrics
# =====================================================

PREDICTION_COUNT = Counter(
    "prediction_requests_total",
    "Total Prediction Requests"
)

PREDICTION_SUCCESS = Counter(
    "prediction_success_total",
    "Successful Predictions"
)

PREDICTION_FAILURE = Counter(
    "prediction_failure_total",
    "Failed Predictions"
)

# =====================================================
# ML Model Metrics
# =====================================================

MODEL_ACCURACY = Gauge(
    "model_accuracy",
    "Random Forest Model Accuracy"
)

MODEL_VERSION = Gauge(
    "model_version",
    "Current Model Version"
)

# =====================================================
# Application Metrics
# =====================================================

APPLICATION_UPTIME = Gauge(
    "application_uptime_seconds",
    "DeployGuard API Uptime in Seconds"
)