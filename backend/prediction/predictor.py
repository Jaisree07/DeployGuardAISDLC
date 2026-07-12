import joblib
import pandas as pd


class Predictor:

    def __init__(self):

        self.rf = joblib.load(
            "ml/saved_models/random_forest.pkl"
        )

        self.iso = joblib.load(
            "ml/saved_models/isolation_forest.pkl"
        )

    def predict(self, request):

        df = pd.DataFrame([request])

        prediction = self.rf.predict(df)[0]

        probability = max(
            self.rf.predict_proba(df)[0]
        )

        anomaly = self.iso.predict(df)[0]

        return {

            "prediction":
                "Healthy"
                if prediction == 1
                else "Failure",

            "confidence":
                round(probability * 100, 2),

            "anomaly":
                False if anomaly == 1 else True

        }