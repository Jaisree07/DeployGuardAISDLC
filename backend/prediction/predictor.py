from backend.ml.model_loader import ModelLoader
from backend.ml.anomaly_detector import AnomalyDetector

from backend.ai.ai_service import AIService


class Predictor:

    ENVIRONMENT = {
        "DEV": 0,
        "QA": 1,
        "UAT": 2,
        "PROD": 3
    }

    @staticmethod
    def predict(data):

        env = Predictor.ENVIRONMENT.get(
            data["environment"],
            0
        )

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
            int(data["error_count"] > 0)

        ]


        prediction, confidence = ModelLoader.predict(features)

        anomaly = AnomalyDetector.predict([
            data["cpu_usage"],
            data["memory_usage"],
            data["latency"],
            data["error_count"]
        ])

        if prediction == 1:
            status = "Healthy Deployment"
            risk = "Low"
        else:
            status = "Deployment Failure"
            risk = "Critical"


        ai_input = {

            "environment": data["environment"],

            "prediction": status,

            "confidence": confidence,

            "risk": risk,

            "anomaly": anomaly,

            "cpu_usage": data["cpu_usage"],

            "memory_usage": data["memory_usage"],

            "latency": data["latency"],

            "build_duration": data["build_duration"],

            "deployment_duration": data["deployment_duration"],

            "error_count": data["error_count"]

        }

        ai_explanation = AIService.generate(ai_input)


        return {

            "prediction": status,

            "confidence": confidence,

            "risk": risk,

            "anomaly": anomaly,

            "model_version": "RandomForest_v1",

            "ai_explanation": ai_explanation

        }