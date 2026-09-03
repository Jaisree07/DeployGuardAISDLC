from backend.prediction.predictor import Predictor


def test_telemetry_has_no_null_values():
    telemetry = {
        "environment": "QA",
        "cpu_usage": 45.0,
        "memory_usage": 50.0,
        "latency": 120.0,
        "build_duration": 30.0,
        "deployment_duration": 60.0,
        "error_count": 0,
    }

    assert all(value is not None for value in telemetry.values())


def test_telemetry_numeric_fields_are_valid():
    telemetry = {
        "cpu_usage": 45.0,
        "memory_usage": 50.0,
        "latency": 120.0,
        "build_duration": 30.0,
        "deployment_duration": 60.0,
        "error_count": 0,
    }

    numeric_fields = [
        "cpu_usage",
        "memory_usage",
        "latency",
        "build_duration",
        "deployment_duration",
        "error_count",
    ]

    for field in numeric_fields:
        assert isinstance(telemetry[field], (int, float))
        assert telemetry[field] >= 0


def test_environment_value_is_valid():
    valid_environments = {"DEV", "QA", "UAT", "PROD"}

    for environment in valid_environments:
        assert Predictor.ENVIRONMENT.get(environment) is not None


def test_threshold_signal_normalization():
    data = {
        "cpu_usage": 85.0,
        "memory_usage": 90.0,
        "latency": 600.0,
        "error_count": 2,
    }

    cpu_signal = int(data["cpu_usage"] > 80)
    memory_signal = int(data["memory_usage"] > 80)
    latency_signal = int(data["latency"] > 500)
    error_signal = int(data["error_count"] > 0)

    assert cpu_signal == 1
    assert memory_signal == 1
    assert latency_signal == 1
    assert error_signal == 1


def test_normal_telemetry_thresholds():
    data = {
        "cpu_usage": 40.0,
        "memory_usage": 50.0,
        "latency": 100.0,
        "error_count": 0,
    }

    assert int(data["cpu_usage"] > 80) == 0
    assert int(data["memory_usage"] > 80) == 0
    assert int(data["latency"] > 500) == 0
    assert int(data["error_count"] > 0) == 0


def test_feature_vector_consistency():
    data = {
        "environment": "QA",
        "cpu_usage": 45.0,
        "memory_usage": 50.0,
        "latency": 120.0,
        "build_duration": 30.0,
        "deployment_duration": 60.0,
        "error_count": 0,
    }

    env = Predictor.ENVIRONMENT.get(data["environment"], 0)

    features = [
        env,
        data["cpu_usage"],
        data["memory_usage"],
        data["latency"],
        data["build_duration"],
        data["deployment_duration"],
        data["error_count"],
        int(data["cpu_usage"] > 80),
        int(data["memory_usage"] > 80),
        int(data["latency"] > 500),
        int(data["error_count"] > 0),
    ]

    assert len(features) == 11
    assert all(isinstance(value, (int, float)) for value in features)
