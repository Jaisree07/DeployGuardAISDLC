from fastapi import APIRouter

from backend.monitoring.prometheus import PREDICTION_COUNT
from backend.schemas.predict import PredictionRequest
from backend.prediction.predictor import Predictor

router = APIRouter(
    prefix="/predict",
    tags=["Prediction"]
)

predictor = Predictor()


@router.post("/")
def predict(request: PredictionRequest):
    # Increment prediction request counter
    PREDICTION_COUNT.inc()

    # Run prediction
    prediction = predictor.predict(
        request.model_dump()
    )

    return prediction