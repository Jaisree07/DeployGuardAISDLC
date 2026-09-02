from fastapi import APIRouter, HTTPException

from backend.schemas.predict import PredictionRequest
from backend.prediction.predictor import Predictor

from backend.monitoring.prometheus import (
    PREDICTION_COUNT,
    PREDICTION_SUCCESS,
    PREDICTION_FAILURE,
    MODEL_ACCURACY,
    MODEL_VERSION,
    DEPLOYMENT_CPU,
    DEPLOYMENT_MEMORY,
    DEPLOYMENT_LATENCY,
    DEPLOYMENT_BUILD_DURATION,
    DEPLOYMENT_DURATION,
    DEPLOYMENT_ERROR_COUNT,
    PREDICTED_RISK,
    ANOMALY_DETECTED,
)

router = APIRouter(
    prefix="/predict",
    tags=["Prediction"]
)


@router.post("/")
def predict(request: PredictionRequest):

    try:
        # =====================================================
        # Count prediction request
        # =====================================================

        PREDICTION_COUNT.inc()

        # =====================================================
        # Record deployment signals
        # =====================================================

        DEPLOYMENT_CPU.set(request.cpu_usage)
        DEPLOYMENT_MEMORY.set(request.memory_usage)
        DEPLOYMENT_LATENCY.set(request.latency)
        DEPLOYMENT_BUILD_DURATION.set(request.build_duration)
        DEPLOYMENT_DURATION.set(request.deployment_duration)
        DEPLOYMENT_ERROR_COUNT.set(request.error_count)

        # =====================================================
        # Run ML prediction
        # =====================================================

        result = Predictor.predict(
            request.model_dump()
        )

        # =====================================================
        # Update model metrics
        # =====================================================

        MODEL_ACCURACY.set(0.97)
        MODEL_VERSION.set(1)

        # =====================================================
        # Update prediction result metrics
        # =====================================================

        if result["prediction"] == "Healthy Deployment":
            PREDICTION_SUCCESS.inc()
        else:
            PREDICTION_FAILURE.inc()

        # =====================================================
        # Determine predicted risk
        # =====================================================

        prediction = result.get("prediction", "")
        confidence = result.get("confidence", 0)

        if prediction == "Healthy Deployment":
            risk_value = 0
        elif confidence >= 0.80:
            risk_value = 2
        else:
            risk_value = 1

        PREDICTED_RISK.set(risk_value)

        # =====================================================
        # Determine anomaly
        # =====================================================

        anomaly = 0

        if (
            request.cpu_usage > 80
            or request.memory_usage > 80
            or request.latency > 500
            or request.error_count > 0
        ):
            anomaly = 1

        ANOMALY_DETECTED.set(anomaly)

        # =====================================================
        # Return prediction
        # =====================================================

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