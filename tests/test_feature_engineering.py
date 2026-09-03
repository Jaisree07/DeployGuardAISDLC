import sqlite3

import pandas as pd
import pytest

from backend.features.feature_engineering import FeatureEngineering


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame(
        [
            {
                "id": 1,
                "deployment_name": "DeployGuard-DEV",
                "environment": "DEV",
                "status": "Running",
                "cpu_usage": 40.0,
                "memory_usage": 50.0,
                "latency": 100.0,
                "build_duration": 60.0,
                "deployment_duration": 30.0,
                "error_count": 0,
            },
            {
                "id": 2,
                "deployment_name": "DeployGuard-PROD",
                "environment": "PROD",
                "status": "Failed",
                "cpu_usage": 90.0,
                "memory_usage": 95.0,
                "latency": 700.0,
                "build_duration": 120.0,
                "deployment_duration": 90.0,
                "error_count": 5,
            },
        ]
    )


# ============================================================
# GENERATE FEATURES
# ============================================================

def test_generate_features(sample_dataframe, monkeypatch):
    """
    Verify feature engineering creates the expected
    target, environment encoding and threshold features.
    """

    monkeypatch.setattr(
        FeatureEngineering,
        "load_signals",
        staticmethod(lambda: sample_dataframe.copy()),
    )

    result = FeatureEngineering.generate_features()

    assert not result.empty

    # Target
    assert "deployment_success" in result.columns

    # Environment encoding
    assert "environment_encoded" in result.columns

    # Engineered features
    assert "high_cpu" in result.columns
    assert "high_memory" in result.columns
    assert "high_latency" in result.columns
    assert "deployment_failed" in result.columns

    # DEV / Running
    assert result.loc[0, "deployment_success"] == 1
    assert result.loc[0, "environment_encoded"] == 0

    # PROD / Failed
    assert result.loc[1, "deployment_success"] == 0
    assert result.loc[1, "environment_encoded"] == 3

    # Normal deployment
    assert result.loc[0, "high_cpu"] == 0
    assert result.loc[0, "high_memory"] == 0
    assert result.loc[0, "high_latency"] == 0
    assert result.loc[0, "deployment_failed"] == 0

    # Risky deployment
    assert result.loc[1, "high_cpu"] == 1
    assert result.loc[1, "high_memory"] == 1
    assert result.loc[1, "high_latency"] == 1
    assert result.loc[1, "deployment_failed"] == 1


def test_generate_features_empty(monkeypatch):
    """
    Verify empty input is handled safely.
    """

    monkeypatch.setattr(
        FeatureEngineering,
        "load_signals",
        staticmethod(lambda: pd.DataFrame()),
    )

    result = FeatureEngineering.generate_features()

    assert result.empty


# ============================================================
# LOAD SIGNALS
# ============================================================

def test_load_signals(monkeypatch, tmp_path):
    """
    Verify deployment and telemetry records are loaded
    and joined correctly from SQLite.
    """

    database = tmp_path / "test.db"

    conn = sqlite3.connect(database)

    conn.execute(
        """
        CREATE TABLE deployments (
            id INTEGER PRIMARY KEY,
            deployment_name TEXT,
            environment TEXT,
            status TEXT
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE telemetry (
            id INTEGER PRIMARY KEY,
            deployment_id INTEGER,
            cpu_usage REAL,
            memory_usage REAL,
            latency REAL,
            build_duration REAL,
            deployment_duration REAL,
            error_count INTEGER
        )
        """
    )

    conn.execute(
        """
        INSERT INTO deployments
        VALUES (1, 'TestDeployment', 'QA', 'Running')
        """
    )

    conn.execute(
        """
        INSERT INTO telemetry
        VALUES (1, 1, 45, 50, 100, 60, 30, 0)
        """
    )

    conn.commit()
    conn.close()

    monkeypatch.setattr(
        FeatureEngineering,
        "DATABASE",
        str(database),
    )

    result = FeatureEngineering.load_signals()

    assert len(result) == 1
    assert result.iloc[0]["deployment_name"] == "TestDeployment"
    assert result.iloc[0]["environment"] == "QA"
    assert result.iloc[0]["cpu_usage"] == 45
    assert result.iloc[0]["latency"] == 100


# ============================================================
# EXPORT DATASET
# ============================================================

def test_export_dataset(sample_dataframe, monkeypatch, tmp_path):
    """
    Verify the engineered dataset is successfully exported
    to datasets/ml_ready_dataset.csv.
    """

    monkeypatch.setattr(
        FeatureEngineering,
        "generate_features",
        staticmethod(lambda: sample_dataframe.copy()),
    )

    # Run the test from an isolated temporary directory.
    monkeypatch.chdir(tmp_path)

    # The production implementation writes to:
    # datasets/ml_ready_dataset.csv
    #
    # Therefore the directory must exist before the
    # production export function is called.
    dataset_directory = tmp_path / "datasets"

    dataset_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    result = FeatureEngineering.export_dataset()

    assert result is not None
    assert not result.empty

    dataset_path = (
        tmp_path
        / "datasets"
        / "ml_ready_dataset.csv"
    )

    assert dataset_path.exists()

    exported = pd.read_csv(dataset_path)

    assert len(exported) == len(result)

    # Verify exported data contains expected columns.
    assert "deployment_name" in exported.columns
    assert "environment" in exported.columns
    assert "cpu_usage" in exported.columns
    assert "memory_usage" in exported.columns
    assert "latency" in exported.columns


def test_export_dataset_empty(monkeypatch, tmp_path):
    """
    Verify no dataset is written when there is no data.
    """

    monkeypatch.setattr(
        FeatureEngineering,
        "generate_features",
        staticmethod(lambda: pd.DataFrame()),
    )

    monkeypatch.chdir(tmp_path)

    # Create the directory so the test remains valid
    # regardless of whether the implementation attempts
    # to access it.
    dataset_directory = tmp_path / "datasets"

    dataset_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    result = FeatureEngineering.export_dataset()

    assert result.empty


# ============================================================
# GET STATISTICS
# ============================================================

def test_get_statistics(sample_dataframe, monkeypatch):
    """
    Verify deployment statistics are calculated correctly.
    """

    dataframe = sample_dataframe.copy()

    # Add the engineered fields expected by get_statistics.
    dataframe["deployment_success"] = (
        dataframe["status"] == "Running"
    ).astype(int)

    dataframe["deployment_failed"] = (
        dataframe["error_count"] > 0
    ).astype(int)

    monkeypatch.setattr(
        FeatureEngineering,
        "generate_features",
        staticmethod(lambda: dataframe),
    )

    result = FeatureEngineering.get_statistics()

    assert result["total_records"] == 2
    assert result["successful_deployments"] == 1
    assert result["failed_deployments"] == 1

    assert result["success_rate"] == 50.0

    assert result["average_cpu"] == 65.0
    assert result["average_memory"] == 72.5
    assert result["average_latency"] == 400.0
    assert result["average_build_duration"] == 90.0
    assert result["average_deployment_duration"] == 60.0


def test_get_statistics_empty(monkeypatch):
    """
    Verify statistics return a meaningful response
    when no deployment data exists.
    """

    monkeypatch.setattr(
        FeatureEngineering,
        "generate_features",
        staticmethod(lambda: pd.DataFrame()),
    )

    result = FeatureEngineering.get_statistics()

    assert result == {
        "message": "No data available."
    }