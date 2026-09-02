import os

from prometheus_client import (
    CollectorRegistry,
    Gauge,
    push_to_gateway,
)


PUSHGATEWAY_URL = os.getenv(
    "PUSHGATEWAY_URL",
    "http://pushgateway:9091"
)


def push_deployment_metrics(
    deployment_name: str,
    cpu_usage: float,
    memory_usage: float,
    latency: float,
    build_duration: float,
    deployment_duration: float,
    error_count: int,
):
    """
    Push deployment telemetry metrics to Prometheus Pushgateway.
    """

    registry = CollectorRegistry()

    # =====================================================
    # Deployment CPU
    # =====================================================

    cpu_metric = Gauge(
        "deployment_cpu_usage_percent",
        "Deployment CPU Usage (%)",
        registry=registry,
    )

    # =====================================================
    # Deployment Memory
    # =====================================================

    memory_metric = Gauge(
        "deployment_memory_usage_percent",
        "Deployment Memory Usage (%)",
        registry=registry,
    )

    # =====================================================
    # Deployment Latency
    # =====================================================

    latency_metric = Gauge(
        "deployment_latency_ms",
        "Deployment Request Latency (ms)",
        registry=registry,
    )

    # =====================================================
    # Build Duration
    # =====================================================

    build_metric = Gauge(
        "deployment_build_duration_seconds",
        "Deployment Build Duration (seconds)",
        registry=registry,
    )

    # =====================================================
    # Deployment Duration
    # =====================================================

    deployment_metric = Gauge(
        "deployment_duration_seconds",
        "Deployment Duration (seconds)",
        registry=registry,
    )

    # =====================================================
    # Error Count
    # =====================================================

    error_metric = Gauge(
        "deployment_error_count",
        "Number of Deployment Errors",
        registry=registry,
    )

    # =====================================================
    # Set Actual Telemetry Values
    # =====================================================

    cpu_metric.set(cpu_usage)

    memory_metric.set(memory_usage)

    latency_metric.set(latency)

    build_metric.set(build_duration)

    deployment_metric.set(deployment_duration)

    error_metric.set(error_count)

    # =====================================================
    # Push Metrics
    # =====================================================

    print(
        f"Pushing deployment metrics to {PUSHGATEWAY_URL}"
    )

    print(f"Deployment: {deployment_name}")

    print(f"CPU Usage: {cpu_usage}%")

    print(f"Memory Usage: {memory_usage}%")

    print(f"Latency: {latency} ms")

    print(
        f"Build Duration: {build_duration} seconds"
    )

    print(
        f"Deployment Duration: "
        f"{deployment_duration} seconds"
    )

    print(f"Error Count: {error_count}")

    push_to_gateway(
        gateway=PUSHGATEWAY_URL,
        job=deployment_name,
        registry=registry,
    )

    print(
        "✅ Deployment telemetry metrics "
        "pushed successfully."
    )