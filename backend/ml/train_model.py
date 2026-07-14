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

        print("=" * 60)
        print("DeployGuard AI - Random Forest Model Training")
        print("=" * 60)

        print("\nLoading Dataset...\n")

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

        print("\nTraining Class Distribution")
        print(y_train.value_counts())

        print("\nTesting Class Distribution")
        print(y_test.value_counts())

        print("\nTraining Random Forest Model...\n")

        model = RandomForestClassifier(
            n_estimators=300,
            max_depth=12,
            min_samples_split=4,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )

        model.fit(X_train, y_train)

        predictions = model.predict(X_test)

        accuracy = accuracy_score(y_test, predictions)
        precision = precision_score(y_test, predictions)
        recall = recall_score(y_test, predictions)
        f1 = f1_score(y_test, predictions)

        print("=" * 60)
        print("MODEL PERFORMANCE")
        print("=" * 60)

        print(f"Accuracy  : {accuracy:.4f}")
        print(f"Precision : {precision:.4f}")
        print(f"Recall    : {recall:.4f}")
        print(f"F1 Score  : {f1:.4f}")

        print("\nConfusion Matrix")
        print(confusion_matrix(y_test, predictions))

        print("\nClassification Report")
        print(classification_report(y_test, predictions))

        print("\nFeature Importance")

        importance = pd.DataFrame({
            "Feature": features,
            "Importance": model.feature_importances_
        })

        importance = importance.sort_values(
            by="Importance",
            ascending=False
        )

        print(importance)

        Path("backend/models_saved").mkdir(
            parents=True,
            exist_ok=True
        )

        joblib.dump(
            model,
            ModelTrainer.MODEL_PATH
        )

        print("\n" + "=" * 60)
        print("MODEL TRAINING COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"Model saved to : {ModelTrainer.MODEL_PATH}")
        print(f"Model Accuracy : {accuracy:.2%}")
        print("=" * 60)


if __name__ == "__main__":
    ModelTrainer.train()