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


# ============================================================
# Helper Functions
# ============================================================

def _get_latest_prediction(
    db: Session,
    deployment_id: int
):
    """
    Return the latest prediction record for a deployment.
    """
    return (
        db.query(Prediction)
        .filter(
            Prediction.deployment_id == deployment_id
        )
        .order_by(
            Prediction.created_at.desc()
        )
        .first()
    )


def _get_latest_telemetry(
    db: Session,
    deployment_id: int
):
    """
    Return the latest telemetry record for a deployment.
    """
    return (
        db.query(Telemetry)
        .filter(
            Telemetry.deployment_id == deployment_id
        )
        .order_by(
            Telemetry.id.desc()
        )
        .first()
    )


# ============================================================
# 1. Latest AI Analysis
# ============================================================

@router.get("/latest-ai-analysis")
def get_latest_ai_analysis(
    db: Session = Depends(get_db)
):
    """
    Return the latest AI-assisted deployment analysis.

    This endpoint is consumed by Grafana to display
    the latest deployment prediction, risk, anomaly,
    telemetry and AI explanation.
    """

    prediction = (
        db.query(Prediction)
        .order_by(
            Prediction.created_at.desc()
        )
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

    telemetry = _get_latest_telemetry(
        db,
        prediction.deployment_id
    )

    return {
        "deployment_id": deployment.id,

        "deployment_name": (
            deployment.deployment_name
        ),

        "version": deployment.version,

        "environment": (
            deployment.environment
        ),

        "deployment_status": (
            deployment.status
        ),

        "prediction": prediction.prediction,

        "confidence": prediction.confidence,

        "risk": prediction.risk,

        "anomaly": prediction.anomaly,

        "ai_explanation": (
            prediction.ai_explanation
        ),

        "created_at": prediction.created_at,

        "telemetry": {
            "cpu_usage": (
                telemetry.cpu_usage
                if telemetry else None
            ),

            "memory_usage": (
                telemetry.memory_usage
                if telemetry else None
            ),

            "latency": (
                telemetry.latency
                if telemetry else None
            ),

            "build_duration": (
                telemetry.build_duration
                if telemetry else None
            ),

            "deployment_duration": (
                telemetry.deployment_duration
                if telemetry else None
            ),

            "error_count": (
                telemetry.error_count
                if telemetry else None
            ),
        }
    }


# ============================================================
# 2. Complete Deployment History
# ============================================================

@router.get("/deployment-history")
def get_deployment_history(
    db: Session = Depends(get_db)
):
    """
    Return the complete deployment history.

    Deployment records are read from the persistent
    SQLite database.

    Each deployment is returned once with its latest
    prediction and latest telemetry information.
    """

    deployments = (
        db.query(Deployment)
        .order_by(
            Deployment.id.desc()
        )
        .all()
    )

    history = []

    for deployment in deployments:

        prediction = _get_latest_prediction(
            db,
            deployment.id
        )

        telemetry = _get_latest_telemetry(
            db,
            deployment.id
        )

        history.append({
            "deployment_id": deployment.id,

            "deployment_name": (
                deployment.deployment_name
            ),

            "version": deployment.version,

            "environment": (
                deployment.environment
            ),

            "deployment_status": (
                deployment.status
            ),

            "prediction": (
                prediction.prediction
                if prediction
                else None
            ),

            "confidence": (
                prediction.confidence
                if prediction
                else None
            ),

            "risk": (
                prediction.risk
                if prediction
                else None
            ),

            "anomaly": (
                prediction.anomaly
                if prediction
                else None
            ),

            "ai_explanation": (
                prediction.ai_explanation
                if prediction
                else None
            ),

            "prediction_created_at": (
                prediction.created_at
                if prediction
                else None
            ),

            "telemetry": {
                "cpu_usage": (
                    telemetry.cpu_usage
                    if telemetry
                    else None
                ),

                "memory_usage": (
                    telemetry.memory_usage
                    if telemetry
                    else None
                ),

                "latency": (
                    telemetry.latency
                    if telemetry
                    else None
                ),

                "build_duration": (
                    telemetry.build_duration
                    if telemetry
                    else None
                ),

                "deployment_duration": (
                    telemetry.deployment_duration
                    if telemetry
                    else None
                ),

                "error_count": (
                    telemetry.error_count
                    if telemetry
                    else None
                ),
            }
        })

    return {
        "total_deployments": len(history),
        "deployments": history
    }


# ============================================================
# 3. Complete AI Analysis History
# ============================================================

@router.get("/ai-analysis-history")
def get_ai_analysis_history(
    db: Session = Depends(get_db)
):
    """
    Return the complete AI-assisted deployment
    analysis history.

    Every prediction record is preserved and linked
    to its corresponding deployment.
    """

    predictions = (
        db.query(Prediction)
        .order_by(
            Prediction.created_at.desc()
        )
        .all()
    )

    history = []

    for prediction in predictions:

        deployment = (
            db.query(Deployment)
            .filter(
                Deployment.id
                == prediction.deployment_id
            )
            .first()
        )

        if deployment is None:
            continue

        history.append({
            "prediction_id": prediction.id,

            "deployment_id": deployment.id,

            "deployment_name": (
                deployment.deployment_name
            ),

            "version": deployment.version,

            "environment": (
                deployment.environment
            ),

            "deployment_status": (
                deployment.status
            ),

            "prediction": (
                prediction.prediction
            ),

            "confidence": (
                prediction.confidence
            ),

            "risk": (
                prediction.risk
            ),

            "anomaly": (
                prediction.anomaly
            ),

            "ai_explanation": (
                prediction.ai_explanation
            ),

            "created_at": (
                prediction.created_at
            )
        })

    return {
        "total_analyses": len(history),
        "analyses": history
    }