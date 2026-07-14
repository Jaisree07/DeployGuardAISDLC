import joblib
import pandas as pd
from pathlib import Path

from sklearn.ensemble import IsolationForest


class AnomalyDetector:

    DATASET = "datasets/ml_ready_dataset.csv"
    MODEL_PATH = "backend/models_saved/isolation_forest_v1.pkl"

    @staticmethod
    def train():

        df = pd.read_csv(AnomalyDetector.DATASET)

        features = [
            "cpu_usage",
            "memory_usage",
            "latency",
            "error_count"
        ]

        X = df[features]

        model = IsolationForest(
            contamination=0.05,
            random_state=42
        )

        model.fit(X)

        Path("backend/models_saved").mkdir(exist_ok=True)

        joblib.dump(model, AnomalyDetector.MODEL_PATH)

        print("Isolation Forest Saved")

    @staticmethod
    def load():
        return joblib.load(AnomalyDetector.MODEL_PATH)

    @staticmethod
    def predict(features):

        model = AnomalyDetector.load()

        result = model.predict([features])[0]

        return "Yes" if result == -1 else "No"


if __name__ == "__main__":
    AnomalyDetector.train()