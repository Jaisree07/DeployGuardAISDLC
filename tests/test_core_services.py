import pytest
from types import SimpleNamespace

from backend.analysis import regression_detector
from backend.services.verification_service import VerificationService


# ============================================================
# Fake SQLAlchemy Query
# ============================================================

class FakeQuery:
    def __init__(self, records):
        self.records = list(records)

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def limit(self, limit):
        self.records = self.records[:limit]
        return self

    def all(self):
        return self.records

    def first(self):
        return self.records[0] if self.records else None


class FakeTelemetryQuery(FakeQuery):
    pass


# ============================================================
# Fake Database
# ============================================================

class FakeDB:
    def __init__(self, deployments=None, telemetry=None):
        self.deployments = deployments or []
        self.telemetry = telemetry or []

    def query(self, model):
        model_name = getattr(model, "__name__", str(model))

        if model_name == "Deployment":
            return FakeQuery(self.deployments)

        if model_name == "Telemetry":
            return FakeTelemetryQuery(self.telemetry)

        return FakeQuery([])


# ============================================================
# Helper Functions
# ============================================================

def make_deployment(
    deployment_id,
    environment="QA",
    status="Running",
):
    return SimpleNamespace(
        id=deployment_id,
        deployment_name=f"Deployment-{deployment_id}",
        version="1.0.0",
        environment=environment,
        status=status,
    )


def make_telemetry(
    deployment_id,
    deployment_duration=100,
    cpu_usage=50,
    memory_usage=50,
    latency=100,
    build_duration=60,
    error_count=0,
):
    return SimpleNamespace(
        deployment_id=deployment_id,
        deployment_duration=deployment_duration,
        cpu_usage=cpu_usage,
        memory_usage=memory_usage,
        latency=latency,
        build_duration=build_duration,
        error_count=error_count,
    )


# ============================================================
# VerificationService Risk Mapping
# ============================================================

def test_risk_value_low():
    assert VerificationService._risk_value("LOW") == 0


def test_risk_value_medium():
    assert VerificationService._risk_value("MEDIUM") == 1


def test_risk_value_high():
    assert VerificationService._risk_value("HIGH") == 2


def test_risk_value_critical():
    assert VerificationService._risk_value("CRITICAL") == 2


def test_risk_value_unknown():
    assert VerificationService._risk_value("UNKNOWN") == 1


# ============================================================
# Regression Detector - Recent Deployments
# ============================================================

def test_recent_deployments():
    deployments = [
        make_deployment(1),
        make_deployment(2),
        make_deployment(3),
        make_deployment(4),
        make_deployment(5),
    ]

    db = FakeDB(deployments=deployments)

    result = regression_detector._recent_deployments(
        db,
        "QA",
        limit=3,
    )

    assert len(result) == 3
    assert result[0].id == 1
    assert result[1].id == 2
    assert result[2].id == 3


# ============================================================
# Regression Detector - Telemetry
# ============================================================

def test_get_telemetry():
    telemetry = [
        make_telemetry(1, deployment_duration=100),
        make_telemetry(2, deployment_duration=200),
    ]

    db = FakeDB(telemetry=telemetry)

    result = regression_detector._get_telemetry(
        db,
        deployment_id=2,
    )

    assert result is not None
    assert result.deployment_id == 2
    assert result.deployment_duration == 200


def test_get_telemetry_not_found():
    db = FakeDB(telemetry=[])

    result = regression_detector._get_telemetry(
        db,
        deployment_id=999,
    )

    assert result is None


# ============================================================
# Baseline Average
# ============================================================

def test_baseline_average():
    deployments = [
        make_deployment(1),
        make_deployment(2),
        make_deployment(3),
        make_deployment(4),
    ]

    telemetry = [
        make_telemetry(1, deployment_duration=100),
        make_telemetry(2, deployment_duration=200),
        make_telemetry(3, deployment_duration=300),
        make_telemetry(4, deployment_duration=400),
    ]

    db = FakeDB(
        deployments=deployments,
        telemetry=telemetry,
    )

    average, count = regression_detector._baseline_average(
        db,
        deployments,
        "deployment_duration",
    )

    assert average == 250
    assert count == 4


def test_baseline_average_no_telemetry():
    deployments = [
        make_deployment(1),
        make_deployment(2),
    ]

    db = FakeDB(
        deployments=deployments,
        telemetry=[],
    )

    average, count = regression_detector._baseline_average(
        db,
        deployments,
        "deployment_duration",
    )

    assert average is None
    assert count == 0


# ============================================================
# Performance Regression
# ============================================================

def test_performance_regression_not_enough_deployments():
    deployments = [
        make_deployment(1),
        make_deployment(2),
        make_deployment(3),
    ]

    db = FakeDB(deployments=deployments)

    result = regression_detector.detect_performance_regression(
        db,
        "QA",
    )

    assert result is None


def test_performance_regression_detected():
    deployments = [
        make_deployment(1),
        make_deployment(2),
        make_deployment(3),
        make_deployment(4),
    ]

    telemetry = [
        make_telemetry(1, deployment_duration=100),
        make_telemetry(2, deployment_duration=100),
        make_telemetry(3, deployment_duration=100),
        make_telemetry(4, deployment_duration=150),
    ]

    db = FakeDB(
        deployments=deployments,
        telemetry=telemetry,
    )

    result = regression_detector.detect_performance_regression(
        db,
        "QA",
    )

    assert result is not None
    assert result["deployment_id"] == 4
    assert result["pattern"] == "performance_regression"
    assert result["severity"] in ["MEDIUM", "HIGH"]


def test_performance_regression_below_threshold():
    deployments = [
        make_deployment(1),
        make_deployment(2),
        make_deployment(3),
        make_deployment(4),
    ]

    telemetry = [
        make_telemetry(1, deployment_duration=100),
        make_telemetry(2, deployment_duration=100),
        make_telemetry(3, deployment_duration=100),
        make_telemetry(4, deployment_duration=120),
    ]

    db = FakeDB(
        deployments=deployments,
        telemetry=telemetry,
    )

    result = regression_detector.detect_performance_regression(
        db,
        "QA",
    )

    assert result is None


# ============================================================
# CPU Regression
# ============================================================

def test_cpu_regression_detected():
    deployments = [
        make_deployment(1),
        make_deployment(2),
        make_deployment(3),
        make_deployment(4),
    ]

    telemetry = [
        make_telemetry(1, cpu_usage=40),
        make_telemetry(2, cpu_usage=40),
        make_telemetry(3, cpu_usage=40),
        make_telemetry(4, cpu_usage=60),
    ]

    db = FakeDB(
        deployments=deployments,
        telemetry=telemetry,
    )

    result = regression_detector.detect_cpu_regression(
        db,
        "QA",
    )

    assert result is not None
    assert result["deployment_id"] == 4
    assert result["pattern"] == "cpu_regression"


# ============================================================
# Memory Regression
# ============================================================

def test_memory_regression_detected():
    deployments = [
        make_deployment(1),
        make_deployment(2),
        make_deployment(3),
        make_deployment(4),
    ]

    telemetry = [
        make_telemetry(1, memory_usage=40),
        make_telemetry(2, memory_usage=40),
        make_telemetry(3, memory_usage=40),
        make_telemetry(4, memory_usage=60),
    ]

    db = FakeDB(
        deployments=deployments,
        telemetry=telemetry,
    )

    result = regression_detector.detect_memory_regression(
        db,
        "QA",
    )

    assert result is not None
    assert result["deployment_id"] == 4
    assert result["pattern"] == "memory_regression"


# ============================================================
# Latency Regression
# ============================================================

def test_latency_regression_detected():
    deployments = [
        make_deployment(1),
        make_deployment(2),
        make_deployment(3),
        make_deployment(4),
    ]

    telemetry = [
        make_telemetry(1, latency=100),
        make_telemetry(2, latency=100),
        make_telemetry(3, latency=100),
        make_telemetry(4, latency=160),
    ]

    db = FakeDB(
        deployments=deployments,
        telemetry=telemetry,
    )

    result = regression_detector.detect_latency_regression(
        db,
        "QA",
    )

    assert result is not None
    assert result["deployment_id"] == 4
    assert result["pattern"] == "latency_regression"


# ============================================================
# Reliability Regression
# ============================================================

def test_reliability_regression_detected():
    deployments = [
        make_deployment(1, status="Running"),
        make_deployment(2, status="Running"),
        make_deployment(3, status="Running"),
        make_deployment(4, status="Failed"),
    ]

    db = FakeDB(deployments=deployments)

    result = regression_detector.detect_reliability_regression(
        db,
        "QA",
    )

    assert result is not None
    assert result["deployment_id"] == 4
    assert result["pattern"] == "reliability_regression"


def test_reliability_regression_not_detected():
    deployments = [
        make_deployment(1, status="Running"),
        make_deployment(2, status="Running"),
        make_deployment(3, status="Running"),
        make_deployment(4, status="Running"),
    ]

    db = FakeDB(deployments=deployments)

    result = regression_detector.detect_reliability_regression(
        db,
        "QA",
    )

    assert result is None


# ============================================================
# Regression History
# ============================================================

def test_regression_history_empty(monkeypatch):
    monkeypatch.setattr(
        regression_detector,
        "detect_all_patterns",
        lambda db, environment: [],
    )

    db = FakeDB()

    result = regression_detector.get_regression_history(
        db,
        "QA",
    )

    assert result == []


# ============================================================
# Dashboard Metric Publishing
# ============================================================

def test_publish_dashboard_metrics_without_regression(monkeypatch):
    deployment = make_deployment(
        10,
        environment="QA",
        status="Running",
    )

    prediction_result = {
        "risk": "LOW",
        "anomaly": "Normal",
        "prediction": "Healthy Deployment",
    }

    monkeypatch.setattr(
        "backend.services.verification_service.DEPLOYMENT_INFO",
        SimpleNamespace(
            labels=lambda *args: SimpleNamespace(
                set=lambda value: None
            )
        ),
    )

    monkeypatch.setattr(
        "backend.services.verification_service.DEPLOYMENT_RISK",
        SimpleNamespace(
            labels=lambda *args: SimpleNamespace(
                set=lambda value: None
            )
        ),
    )

    monkeypatch.setattr(
        "backend.services.verification_service.REGRESSION_DETECTED",
        SimpleNamespace(
            labels=lambda *args: SimpleNamespace(
                set=lambda value: None,
                remove=lambda *args: None,
            )
        ),
    )

    VerificationService._publish_dashboard_metrics(
        deployment,
        prediction_result,
        [],
    )


def test_publish_dashboard_metrics_with_regression(monkeypatch):
    deployment = make_deployment(
        11,
        environment="QA",
        status="BLOCKED",
    )

    prediction_result = {
        "risk": "HIGH",
        "anomaly": "Anomaly",
        "prediction": "Deployment Failure",
    }

    regression = {
        "deployment_id": 11,
        "pattern": "latency_regression",
        "severity": "HIGH",
    }

    monkeypatch.setattr(
        "backend.services.verification_service.DEPLOYMENT_INFO",
        SimpleNamespace(
            labels=lambda *args: SimpleNamespace(
                set=lambda value: None
            )
        ),
    )

    monkeypatch.setattr(
        "backend.services.verification_service.DEPLOYMENT_RISK",
        SimpleNamespace(
            labels=lambda *args: SimpleNamespace(
                set=lambda value: None
            )
        ),
    )

    monkeypatch.setattr(
        "backend.services.verification_service.REGRESSION_DETECTED",
        SimpleNamespace(
            labels=lambda *args: SimpleNamespace(
                set=lambda value: None,
                remove=lambda *args: None,
            )
        ),
    )

    VerificationService._publish_dashboard_metrics(
        deployment,
        prediction_result,
        [regression],
    )


# ============================================================
# Save Prediction
# ============================================================

def test_save_prediction():
    class FakeSession:
        def __init__(self):
            self.added = None

        def add(self, value):
            self.added = value

        def commit(self):
            pass

        def refresh(self, value):
            value.id = 1

    db = FakeSession()

    deployment = make_deployment(1)

    prediction_result = {
        "prediction": "Healthy Deployment",
        "confidence": 0.95,
        "anomaly": "Normal",
        "risk": "LOW",
        "ai_explanation": "Deployment appears healthy.",
    }

    result = VerificationService._save_prediction(
        db,
        deployment,
        prediction_result,
    )

    assert result is not None
    assert result.id == 1
    assert db.added is result
    assert result.deployment_id == deployment.id
    assert result.prediction == "Healthy Deployment"
    assert result.confidence == 0.95
    assert result.anomaly == "Normal"
    assert result.risk == "LOW"
    assert result.ai_explanation == "Deployment appears healthy."