import joblib
from pathlib import Path


class ModelLoader:

    MODEL_PATH = Path("backend/models_saved/random_forest_v1.pkl")

    _model = None

    @classmethod
    def load_model(cls):
        """
        Load the trained model only once.
        """

        if cls._model is None:

            if not cls.MODEL_PATH.exists():
                raise FileNotFoundError(
                    f"Model file not found: {cls.MODEL_PATH}"
                )

            print(f"Loading model from: {cls.MODEL_PATH}")

            cls._model = joblib.load(cls.MODEL_PATH)

            print("Model loaded successfully.")

        return cls._model

    @classmethod
    def predict(cls, features):
        """
        Predict deployment outcome and confidence.
        """

        model = cls.load_model()

        prediction = model.predict([features])[0]

        probability = model.predict_proba([features])[0]

        confidence = round(max(probability) * 100, 2)

        return prediction, confidence