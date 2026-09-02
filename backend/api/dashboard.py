from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.models.prediction import Prediction
from backend.models.deployment import Deployment
from backend.models.telemetry import Telemetry


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/latest-ai-analysis")
def get_latest_ai_analysis(
    db: Session = Depends(get_db)
):
    """
    Return the latest AI-assisted deployment analysis.

    This endpoint is consumed by Grafana to display
    the real-time AI explanation for the latest
    verified deployment.
    """

    prediction = (
        db.query(Prediction)
        .order_by(Prediction.created_at.desc())
        .first()
    )

    if prediction is None:
        raise HTTPException(
            status_code=404,
            detail="No AI deployment analysis found"
        )

    deployment = (
        db.query(Deployment)
        .filter(
            Deployment.id == prediction.deployment_id
        )
        .first()
    )

    if deployment is None:
        raise HTTPException(
            status_code=404,
            detail="Deployment not found"
        )

    telemetry = (
        db.query(Telemetry)
        .filter(
            Telemetry.deployment_id
            == prediction.deployment_id
        )
        .order_by(
            Telemetry.id.desc()
        )
        .first()
    )

    return {
        "deployment_id": deployment.id,

        "deployment_name": deployment.deployment_name,

        "version": deployment.version,

        "environment": deployment.environment,

        "deployment_status": deployment.status,

        "prediction": prediction.prediction,

        "confidence": prediction.confidence,

        "risk": prediction.risk,

        "anomaly": prediction.anomaly,

        "ai_explanation": prediction.ai_explanation,

        "created_at": prediction.created_at,

        "telemetry": {
            "cpu_usage": telemetry.cpu_usage
            if telemetry else None,

            "memory_usage": telemetry.memory_usage
            if telemetry else None,

            "latency": telemetry.latency
            if telemetry else None,

            "build_duration": telemetry.build_duration
            if telemetry else None,

            "deployment_duration": telemetry.deployment_duration
            if telemetry else None,

            "error_count": telemetry.error_count
            if telemetry else None,
        }
    }