import joblib


class ModelLoader:

    MODEL_PATH = "backend/models_saved/random_forest_v1.pkl"

    model = joblib.load(MODEL_PATH)

    @staticmethod
    def predict(features):

        prediction = ModelLoader.model.predict([features])[0]

        probability = ModelLoader.model.predict_proba([features])[0]

        confidence = round(max(probability) * 100, 2)

        return prediction, confidence