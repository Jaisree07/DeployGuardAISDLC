import os
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

PUSHGATEWAY_URL = os.getenv(
    "PUSHGATEWAY_URL",
    "http://pushgateway:9091"
)


def push_deployment_metrics(
    deployment_name: str,
    build_duration: float,
    deployment_duration: float,
):
    registry = CollectorRegistry()

    build_metric = Gauge(
        "build_duration_seconds",
        "Build Duration",
        registry=registry,
    )

    deployment_metric = Gauge(
        "deployment_duration_seconds",
        "Deployment Duration",
        registry=registry,
    )

    build_metric.set(build_duration)
    deployment_metric.set(deployment_duration)

    print(f"Pushing metrics to {PUSHGATEWAY_URL}")

    push_to_gateway(
        gateway=PUSHGATEWAY_URL,
        job=deployment_name,
        registry=registry,
    )

    print("✅ Metrics pushed successfully.")
