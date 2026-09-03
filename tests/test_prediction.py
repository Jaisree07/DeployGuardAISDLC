import pytest

from backend.prediction.predictor import Predictor
from backend.ai.ai_service import AIService


# ---------------------------------------------------------
# Predictor tests
# ---------------------------------------------------------

@pytest.fixture
def healthy_data():
    return {
        "environment": "QA",
        "cpu_usage": 45.0,
        "memory_usage": 50.0,
        "latency": 120.0,
        "build_duration": 60.0,
        "deployment_duration": 30.0,
        "error_count": 0,
    }


@pytest.fixture
def risky_data():
    return {
        "environment": "PROD",
        "cpu_usage": 95.0,
        "memory_usage": 92.0,
        "latency": 800.0,
        "build_duration": 300.0,
        "deployment_duration": 180.0,
        "error_count": 10,
    }


def test_predictor_healthy_deployment(monkeypatch, healthy_data):
    """
    Verify that a successful ML prediction is converted
    into a Healthy Deployment with Low risk.
    """

    monkeypatch.setattr(
        "backend.prediction.predictor.ModelLoader.predict",
        lambda features: (1, 0.95)
    )

    monkeypatch.setattr(
        "backend.prediction.predictor.AnomalyDetector.predict",
        lambda features: 0
    )

    monkeypatch.setattr(
        "backend.prediction.predictor.AIService.generate",
        lambda pattern: "Healthy deployment explanation"
    )

    result = Predictor.predict(healthy_data)

    assert result["prediction"] == "Healthy Deployment"
    assert result["confidence"] == 0.95
    assert result["risk"] == "Low"
    assert result["anomaly"] == 0
    assert result["model_version"] == "RandomForest_v1"
    assert result["ai_explanation"] == "Healthy deployment explanation"


def test_predictor_failed_deployment(monkeypatch, risky_data):
    """
    Verify that a failed ML prediction is converted
    into Deployment Failure with Critical risk.
    """

    monkeypatch.setattr(
        "backend.prediction.predictor.ModelLoader.predict",
        lambda features: (0, 0.90)
    )

    monkeypatch.setattr(
        "backend.prediction.predictor.AnomalyDetector.predict",
        lambda features: 1
    )

    monkeypatch.setattr(
        "backend.prediction.predictor.AIService.generate",
        lambda pattern: "Risky deployment explanation"
    )

    result = Predictor.predict(risky_data)

    assert result["prediction"] == "Deployment Failure"
    assert result["confidence"] == 0.90
    assert result["risk"] == "Critical"
    assert result["anomaly"] == 1
    assert result["model_version"] == "RandomForest_v1"
    assert result["ai_explanation"] == "Risky deployment explanation"


def test_predictor_environment_mapping(monkeypatch, healthy_data):
    """
    Verify that environment values are translated correctly
    before ML prediction.
    """

    captured_features = {}

    def fake_predict(features):
        captured_features["features"] = features
        return 1, 0.88

    monkeypatch.setattr(
        "backend.prediction.predictor.ModelLoader.predict",
        fake_predict
    )

    monkeypatch.setattr(
        "backend.prediction.predictor.AnomalyDetector.predict",
        lambda features: 0
    )

    monkeypatch.setattr(
        "backend.prediction.predictor.AIService.generate",
        lambda pattern: "Test explanation"
    )

    Predictor.predict(healthy_data)

    features = captured_features["features"]

    # QA = 1
    assert features[0] == 1

    # Original telemetry values
    assert features[1] == 45.0
    assert features[2] == 50.0
    assert features[3] == 120.0
    assert features[4] == 60.0
    assert features[5] == 30.0
    assert features[6] == 0

    # Threshold flags
    assert features[7] == 0  # CPU > 80
    assert features[8] == 0  # Memory > 80
    assert features[9] == 0  # Latency > 500
    assert features[10] == 0  # Errors > 0


def test_predictor_threshold_features(monkeypatch, risky_data):
    """
    Verify that high CPU, memory, latency and error values
    activate the corresponding engineered features.
    """

    captured_features = {}

    def fake_predict(features):
        captured_features["features"] = features
        return 0, 0.91

    monkeypatch.setattr(
        "backend.prediction.predictor.ModelLoader.predict",
        fake_predict
    )

    monkeypatch.setattr(
        "backend.prediction.predictor.AnomalyDetector.predict",
        lambda features: 1
    )

    monkeypatch.setattr(
        "backend.prediction.predictor.AIService.generate",
        lambda pattern: "Risk explanation"
    )

    Predictor.predict(risky_data)

    features = captured_features["features"]

    assert features[0] == 3       # PROD
    assert features[7] == 1       # CPU > 80
    assert features[8] == 1       # Memory > 80
    assert features[9] == 1       # Latency > 500
    assert features[10] == 1      # Error count > 0


# ---------------------------------------------------------
# AIService tests
# ---------------------------------------------------------

def test_ai_service_primary_provider(monkeypatch):
    """
    Verify that the configured primary AI provider is used.
    """

    monkeypatch.setattr(
        "backend.ai.ai_service.AIConfig.PROVIDER",
        "groq"
    )

    monkeypatch.setattr(
        "backend.ai.ai_service.AIConfig.FALLBACK_ORDER",
        ["ollama"]
    )

    monkeypatch.setattr(
        "backend.ai.ai_service._PROVIDERS",
        {
            "groq": lambda prompt: "Groq explanation",
            "ollama": lambda prompt: "Ollama explanation",
        }
    )

    monkeypatch.setattr(
        "backend.ai.ai_service.build_prompt",
        lambda pattern: "test prompt"
    )

    result = AIService.generate({"risk": "Low"})

    assert result == "Groq explanation"


def test_ai_service_fallback_provider(monkeypatch):
    """
    Verify that the fallback provider is used when
    the primary AI provider fails.
    """

    monkeypatch.setattr(
        "backend.ai.ai_service.AIConfig.PROVIDER",
        "groq"
    )

    monkeypatch.setattr(
        "backend.ai.ai_service.AIConfig.FALLBACK_ORDER",
        ["ollama"]
    )

    def failed_groq(prompt):
        raise RuntimeError("Groq unavailable")

    monkeypatch.setattr(
        "backend.ai.ai_service._PROVIDERS",
        {
            "groq": failed_groq,
            "ollama": lambda prompt: "Ollama fallback explanation",
        }
    )

    monkeypatch.setattr(
        "backend.ai.ai_service.build_prompt",
        lambda pattern: "test prompt"
    )

    result = AIService.generate({"risk": "Critical"})

    assert result == "Ollama fallback explanation"


def test_ai_service_all_providers_fail(monkeypatch):
    """
    Verify graceful handling when all AI providers fail.
    """

    monkeypatch.setattr(
        "backend.ai.ai_service.AIConfig.PROVIDER",
        "groq"
    )

    monkeypatch.setattr(
        "backend.ai.ai_service.AIConfig.FALLBACK_ORDER",
        ["ollama"]
    )

    def failed_provider(prompt):
        raise RuntimeError("Provider unavailable")

    monkeypatch.setattr(
        "backend.ai.ai_service._PROVIDERS",
        {
            "groq": failed_provider,
            "ollama": failed_provider,
        }
    )

    monkeypatch.setattr(
        "backend.ai.ai_service.build_prompt",
        lambda pattern: "test prompt"
    )

    result = AIService.generate({"risk": "Critical"})

    assert "[AI explanation unavailable" in result
    assert "Raw pattern" in result


def test_ai_service_explain_all(monkeypatch):
    """
    Verify that multiple deployment patterns are explained.
    """

    monkeypatch.setattr(
        AIService,
        "generate",
        staticmethod(lambda pattern: f"Explanation for {pattern['name']}")
    )

    patterns = [
        {"name": "deployment_1"},
        {"name": "deployment_2"},
        {"name": "deployment_3"},
    ]

    result = AIService.explain_all(patterns)

    assert len(result) == 3
    assert result[0]["pattern"] == patterns[0]
    assert result[0]["explanation"] == "Explanation for deployment_1"
    assert result[1]["explanation"] == "Explanation for deployment_2"
    assert result[2]["explanation"] == "Explanation for deployment_3"
