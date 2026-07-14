from fastapi import APIRouter, HTTPException

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

    try:

        # Count every prediction request
        PREDICTION_COUNT.inc()

        # Get prediction from ML model
        result = Predictor.predict(
            request.model_dump()
        )

        # Update model metrics
        MODEL_ACCURACY.set(0.97)
        MODEL_VERSION.set(1)

        # Update prediction counters
        if result["prediction"] == "Healthy Deployment":
            PREDICTION_SUCCESS.inc()
        else:
            PREDICTION_FAILURE.inc()

        return {
            "success": True,
            "message": "Prediction generated successfully.",
            "data": result
        }

    except Exception as e:

        PREDICTION_FAILURE.inc()

        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )