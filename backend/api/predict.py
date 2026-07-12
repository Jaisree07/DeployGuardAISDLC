from fastapi import APIRouter

from backend.schemas.predict import PredictionRequest
from backend.prediction.predictor import Predictor

router = APIRouter(
    prefix="/predict",
    tags=["Prediction"]
)

predictor = Predictor()


@router.post("/")
def predict(request: PredictionRequest):

    return predictor.predict(
        request.model_dump()
    )