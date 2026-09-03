from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_application_health_integration():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "Healthy"


def test_application_root_integration():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["application"] == "DeployGuard AI"
    assert data["status"] == "Running"
    assert "version" in data
    assert "environment" in data


def test_prometheus_metrics_integration():
    response = client.get("/metrics")

    assert response.status_code == 200

    assert "http_requests_total" in response.text
    assert "deployguard" in response.text.lower()


def test_deployment_creation_integration():
    deployment_payload = {
        "deployment_name": "Integration-Test-Deployment",
        "version": "1.0.0",
        "environment": "QA",
        "status": "Running",
    }

    response = client.post(
        "/deployments/",
        json=deployment_payload,
    )

    assert response.status_code in [200, 201]

    data = response.json()

    assert "id" in data
    assert data["deployment_name"] == "Integration-Test-Deployment"
    assert data["version"] == "1.0.0"
    assert data["environment"] == "QA"


def test_telemetry_creation_integration():
    deployment_payload = {
        "deployment_name": "Telemetry-Integration-Test",
        "version": "1.0.0",
        "environment": "QA",
        "status": "Running",
    }

    deployment_response = client.post(
        "/deployments/",
        json=deployment_payload,
    )

    assert deployment_response.status_code in [200, 201]

    deployment = deployment_response.json()
    deployment_id = deployment["id"]

    telemetry_payload = {
        "deployment_id": deployment_id,
        "cpu_usage": 40.0,
        "memory_usage": 45.0,
        "latency": 100.0,
        "build_duration": 60.0,
        "deployment_duration": 30.0,
        "error_count": 0,
    }

    response = client.post(
        "/telemetry/",
        json=telemetry_payload,
    )

    assert response.status_code in [200, 201]

    data = response.json()

    assert data is not None


def test_dashboard_data_integration():
    possible_endpoints = [
        "/dashboard/deployments",
        "/dashboard/history",
        "/deployments/",
    ]

    successful_response = None

    for endpoint in possible_endpoints:
        response = client.get(endpoint)

        if response.status_code == 200:
            successful_response = response
            break

    assert successful_response is not None
    assert successful_response.status_code == 200


def test_telemetry_updates_metrics():
    deployment_payload = {
        "deployment_name": "Metrics-Integration-Test",
        "version": "1.0.0",
        "environment": "QA",
        "status": "Running",
    }

    deployment_response = client.post(
        "/deployments/",
        json=deployment_payload,
    )

    assert deployment_response.status_code in [200, 201]

    deployment = deployment_response.json()
    deployment_id = deployment["id"]

    telemetry_payload = {
        "deployment_id": deployment_id,
        "cpu_usage": 55.0,
        "memory_usage": 60.0,
        "latency": 150.0,
        "build_duration": 90.0,
        "deployment_duration": 120.0,
        "error_count": 0,
    }

    telemetry_response = client.post(
        "/telemetry/",
        json=telemetry_payload,
    )

    assert telemetry_response.status_code in [200, 201]

    metrics_response = client.get("/metrics")

    assert metrics_response.status_code == 200

    metrics = metrics_response.text

    assert "deployment_cpu_usage_percent" in metrics
    assert "deployment_memory_usage_percent" in metrics
    assert "deployment_latency_ms" in metrics
    assert "deployment_build_duration_seconds" in metrics
    assert "deployment_duration_seconds" in metrics
    assert "deployment_error_count" in metrics