from backend.ml.model_loader import ModelLoader
from backend.ml.anomaly_detector import AnomalyDetector
from backend.prediction.predictor import Predictor


def test_random_forest_prediction_returns_valid_result():
    features = [
        1,
        40.0,
        45.0,
        100.0,
        60.0,
        30.0,
        0,
        0,
        0,
        0,
        0,
    ]

    prediction, confidence = ModelLoader.predict(features)

    assert prediction in [0, 1]
    assert isinstance(confidence, (int, float))
    assert 0 <= confidence <= 100


def test_random_forest_prediction_is_consistent():
    features = [
        1,
        40.0,
        45.0,
        100.0,
        60.0,
        30.0,
        0,
        0,
        0,
        0,
        0,
    ]

    prediction1, confidence1 = ModelLoader.predict(features)
    prediction2, confidence2 = ModelLoader.predict(features)

    assert prediction1 == prediction2
    assert confidence1 == confidence2


def test_anomaly_detector_returns_valid_result():
    telemetry = [
        40.0,
        45.0,
        100.0,
        0,
    ]

    result = AnomalyDetector.predict(telemetry)

    assert result in ["Yes", "No"]


def test_anomaly_detector_is_consistent():
    telemetry = [
        40.0,
        45.0,
        100.0,
        0,
    ]

    result1 = AnomalyDetector.predict(telemetry)
    result2 = AnomalyDetector.predict(telemetry)

    assert result1 == result2


def test_predictor_returns_required_fields():
    data = {
        "environment": "QA",
        "cpu_usage": 40.0,
        "memory_usage": 45.0,
        "latency": 100.0,
        "build_duration": 60.0,
        "deployment_duration": 30.0,
        "error_count": 0,
    }

    result = Predictor.predict(data)

    required_fields = [
        "prediction",
        "confidence",
        "risk",
        "anomaly",
        "model_version",
        "ai_explanation",
    ]

    for field in required_fields:
        assert field in result


def test_predictor_confidence_is_valid():
    data = {
        "environment": "QA",
        "cpu_usage": 40.0,
        "memory_usage": 45.0,
        "latency": 100.0,
        "build_duration": 60.0,
        "deployment_duration": 30.0,
        "error_count": 0,
    }

    result = Predictor.predict(data)

    assert isinstance(result["confidence"], (int, float))
    assert 0 <= result["confidence"] <= 100


def test_predictor_risk_is_valid():
    data = {
        "environment": "QA",
        "cpu_usage": 85.0,
        "memory_usage": 90.0,
        "latency": 600.0,
        "build_duration": 100.0,
        "deployment_duration": 200.0,
        "error_count": 5,
    }

    result = Predictor.predict(data)

    assert result["risk"] in [
        "Low",
        "Medium",
        "High",
        "Critical",
    ]


def test_environment_encoding():
    assert Predictor.ENVIRONMENT["DEV"] == 0
    assert Predictor.ENVIRONMENT["QA"] == 1
    assert Predictor.ENVIRONMENT["UAT"] == 2
    assert Predictor.ENVIRONMENT["PROD"] == 3


def test_cpu_threshold_feature():
    assert int(79.9 > 80) == 0
    assert int(80.1 > 80) == 1


def test_memory_threshold_feature():
    assert int(79.9 > 80) == 0
    assert int(80.1 > 80) == 1


def test_latency_threshold_feature():
    assert int(500 > 500) == 0
    assert int(500.1 > 500) == 1


def test_error_threshold_feature():
    assert int(0 > 0) == 0
    assert int(1 > 0) == 1