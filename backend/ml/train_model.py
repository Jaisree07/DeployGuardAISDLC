import joblib
import pandas as pd

from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
from sklearn.model_selection import train_test_split


class ModelTrainer:

    DATASET = "datasets/ml_ready_dataset.csv"
    MODEL_PATH = "backend/models_saved/random_forest_v1.pkl"

    @staticmethod
    def train():

        print("\n========== LOADING DATASET ==========\n")

        df = pd.read_csv(ModelTrainer.DATASET)

        print(df.head())

        print("\nDataset Shape:", df.shape)

        features = [
            "environment_encoded",
            "cpu_usage",
            "memory_usage",
            "latency",
            "build_duration",
            "deployment_duration",
            "error_count",
            "high_cpu",
            "high_memory",
            "high_latency",
            "deployment_failed"
        ]

        X = df[features]

        y = df["deployment_success"]

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y
        )

        print("\nTraining Records :", len(X_train))
        print("Testing Records  :", len(X_test))

        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            random_state=42
        )

        model.fit(X_train, y_train)

        predictions = model.predict(X_test)

        print("\n========== MODEL METRICS ==========\n")

        print("Accuracy :", round(accuracy_score(y_test, predictions),4))
        print("Precision:", round(precision_score(y_test, predictions),4))
        print("Recall   :", round(recall_score(y_test, predictions),4))
        print("F1 Score :", round(f1_score(y_test, predictions),4))

        print("\n========== CONFUSION MATRIX ==========\n")
        print(confusion_matrix(y_test, predictions))

        print("\n========== CLASSIFICATION REPORT ==========\n")
        print(classification_report(y_test, predictions))

        print("\n========== FEATURE IMPORTANCE ==========\n")

        importance = pd.DataFrame({
            "Feature": features,
            "Importance": model.feature_importances_
        })

        importance = importance.sort_values(
            by="Importance",
            ascending=False
        )

        print(importance)

        Path("backend/models_saved").mkdir(exist_ok=True)

        joblib.dump(
            model,
            ModelTrainer.MODEL_PATH
        )

        print("\nModel Saved Successfully")
        print(ModelTrainer.MODEL_PATH)


if __name__ == "__main__":
    ModelTrainer.train()