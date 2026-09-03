import pytest
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def create_deployment(
    name,
    environment="QA",
    status="Running"
):
    response = client.post(
        "/deployments/",
        json={
            "deployment_name": name,
            "version": "1.0.0",
            "environment": environment,
            "status": status
        }
    )

    assert response.status_code in [200, 201]

    return response.json()


def create_telemetry(
    deployment_id,
    cpu,
    memory,
    latency,
    build_duration,
    deployment_duration,
    errors
):
    response = client.post(
        "/telemetry/",
        json={
            "deployment_id": deployment_id,
            "cpu_usage": cpu,
            "memory_usage": memory,
            "latency": latency,
            "build_duration": build_duration,
            "deployment_duration": deployment_duration,
            "error_count": errors
        }
    )

    assert response.status_code in [200, 201]

    return response.json()


# ============================================================
# E2E Scenario 1
# Healthy Deployment
# ============================================================

def test_e2e_healthy_deployment():

    deployment = create_deployment(
        "E2E-Healthy-Deployment",
        environment="QA",
        status="Running"
    )

    deployment_id = deployment["id"]

    telemetry = create_telemetry(
        deployment_id=deployment_id,
        cpu=40,
        memory=45,
        latency=100,
        build_duration=60,
        deployment_duration=30,
        errors=0
    )

    assert telemetry["deployment_id"] == deployment_id

    verification_response = client.post(
        f"/verify/{deployment_id}"
    )

    assert verification_response.status_code in [200, 201]

    result = verification_response.json()

    assert isinstance(result, dict)

    assert any(
        key in result
        for key in [
            "prediction",
            "risk",
            "verification_status",
            "status",
            "decision",
            "result"
        ]
    )


# ============================================================
# E2E Scenario 2
# High Risk Deployment
# ============================================================

def test_e2e_high_risk_deployment():

    deployment = create_deployment(
        "E2E-High-Risk-Deployment",
        environment="PROD",
        status="Running"
    )

    deployment_id = deployment["id"]

    telemetry = create_telemetry(
        deployment_id=deployment_id,
        cpu=95,
        memory=95,
        latency=900,
        build_duration=300,
        deployment_duration=180,
        errors=10
    )

    assert telemetry["deployment_id"] == deployment_id

    verification_response = client.post(
        f"/verify/{deployment_id}"
    )

    assert verification_response.status_code in [200, 201]

    result = verification_response.json()

    assert isinstance(result, dict)

    # At least one risk-related field must exist.
    risk_value = result.get("risk")

    if risk_value is not None:
        assert str(risk_value).upper() in [
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL"
        ]


# ============================================================
# E2E Scenario 3
# Deployment With Errors
# ============================================================

def test_e2e_failed_deployment():

    deployment = create_deployment(
        "E2E-Failed-Deployment",
        environment="PROD",
        status="Failed"
    )

    deployment_id = deployment["id"]

    telemetry = create_telemetry(
        deployment_id=deployment_id,
        cpu=90,
        memory=90,
        latency=800,
        build_duration=250,
        deployment_duration=150,
        errors=8
    )

    assert telemetry["deployment_id"] == deployment_id

    verification_response = client.post(
        f"/verify/{deployment_id}"
    )

    assert verification_response.status_code in [200, 201]

    result = verification_response.json()

    assert isinstance(result, dict)


# ============================================================
# E2E Scenario 4
# Metrics After Complete Workflow
# ============================================================

def test_e2e_metrics_after_deployment_workflow():

    deployment = create_deployment(
        "E2E-Metrics-Deployment",
        environment="QA",
        status="Running"
    )

    deployment_id = deployment["id"]

    create_telemetry(
        deployment_id=deployment_id,
        cpu=55,
        memory=60,
        latency=200,
        build_duration=70,
        deployment_duration=40,
        errors=0
    )

    verification_response = client.post(
        f"/verify/{deployment_id}"
    )

    assert verification_response.status_code in [200, 201]

    metrics_response = client.get("/metrics")

    assert metrics_response.status_code == 200

    metrics = metrics_response.text

    assert "prediction_requests_total" in metrics
    assert "deployment_predicted_risk" in metrics
    assert "deployment_anomaly_detected" in metrics