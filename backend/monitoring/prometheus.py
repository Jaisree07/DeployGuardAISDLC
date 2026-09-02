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
# Deployment Signal Metrics
# =====================================================

DEPLOYMENT_CPU = Gauge(
    "deployment_cpu_usage_percent",
    "Deployment CPU Usage (%)"
)

DEPLOYMENT_MEMORY = Gauge(
    "deployment_memory_usage_percent",
    "Deployment Memory Usage (%)"
)

DEPLOYMENT_LATENCY = Gauge(
    "deployment_latency_ms",
    "Deployment Request Latency (ms)"
)

DEPLOYMENT_BUILD_DURATION = Gauge(
    "deployment_build_duration_seconds",
    "Deployment Build Duration (seconds)"
)

DEPLOYMENT_DURATION = Gauge(
    "deployment_duration_seconds",
    "Deployment Duration (seconds)"
)

DEPLOYMENT_ERROR_COUNT = Gauge(
    "deployment_error_count",
    "Number of Deployment Errors"
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
# Deployment Intelligence Metrics
# =====================================================

PREDICTED_RISK = Gauge(
    "deployment_predicted_risk",
    "Predicted Deployment Risk (0=Low, 1=Medium, 2=High)"
)

ANOMALY_DETECTED = Gauge(
    "deployment_anomaly_detected",
    "Deployment Anomaly Detection (0=Normal, 1=Anomaly)"
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


# =====================================================
# Requirement 6 — Per-Deployment Dashboard Metrics
# =====================================================

DEPLOYMENT_INFO = Gauge(
    "deployguard_deployment_info",
    "Deployment information for dashboard history",
    [
        "deployment_id",
        "deployment_name",
        "version",
        "environment",
        "status"
    ]
)

DEPLOYMENT_RISK = Gauge(
    "deployguard_deployment_risk",
    "Predicted ML risk per deployment (0=Low, 1=Medium, 2=High)",
    [
        "deployment_id",
        "deployment_name",
        "environment"
    ]
)

REGRESSION_DETECTED = Gauge(
    "deployguard_regression_detected",
    "Regression detected for a deployment",
    [
        "deployment_id",
        "deployment_name",
        "environment",
        "pattern",
        "severity"
    ]
)