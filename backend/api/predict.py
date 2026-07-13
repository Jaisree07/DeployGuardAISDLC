from fastapi import APIRouter

from backend.schemas.predict import PredictionRequest
from backend.prediction.predictor import Predictor

from backend.monitoring.prometheus import (
    PREDICTION_COUNT,
    PREDICTION_SUCCESS,
    PREDICTION_FAILURE,
    MODEL_ACCURACY,
    MODEL_VERSION
)

router = APIRouter(
    prefix="/predict",
    tags=["Prediction"]
)


@router.post("/")
def predict(request: PredictionRequest):

    # Count every prediction request
    PREDICTION_COUNT.inc()

    # Get prediction from ML model
    result = Predictor.predict(
        request.model_dump()
    )

    # Set model information
    MODEL_ACCURACY.set(0.97)   # Replace with your actual model accuracy
    MODEL_VERSION.set(1)       # Model version

    # Update prediction counters
    if result["prediction"] == "Healthy Deployment":
        PREDICTION_SUCCESS.inc()
    else:
        PREDICTION_FAILURE.inc()

    return result