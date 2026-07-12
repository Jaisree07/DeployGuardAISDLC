import joblib
import pandas as pd

from sklearn.ensemble import (
    RandomForestClassifier,
    IsolationForest
)

from sklearn.model_selection import train_test_split

df = pd.read_csv("datasets/ml_dataset.csv")

features = [

    "cpu_usage",

    "memory_usage",

    "latency",

    "build_duration",

    "deployment_duration",

    "error_count",

    "resource_usage",

    "deployment_speed",

    "failure_risk"

]

X = df[features]

y = df["healthy"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

rf = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

rf.fit(X_train, y_train)

iso = IsolationForest(
    contamination=0.05,
    random_state=42
)

iso.fit(X_train)

joblib.dump(
    rf,
    "ml/saved_models/random_forest.pkl"
)

joblib.dump(
    iso,
    "ml/saved_models/isolation_forest.pkl"
)

print("Models Trained Successfully")