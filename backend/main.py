from fastapi import FastAPI
from fastapi.responses import Response
from sqlalchemy import inspect, text

from backend.api.regressions import router as regressions_router
from backend.api.features import router as feature_router
from backend.api.signals import router as signals_router
from backend.storage.sqlite_storage import SQLiteStorage
from backend.api.telemetry import router as telemetry_router
from backend.api.deployment import router as deployment_router
from backend.core.config import settings
from backend.core.logger import logger
from backend.database.database import Base, engine
from backend.models.deployment import Deployment
from backend.models.telemetry import Telemetry
from backend.api.predict import router as predict_router
from backend.api.verification import router as verification_router
from backend.models.prediction import Prediction
from backend.middleware.metrics import MetricsMiddleware
from backend.api.dashboard import router as dashboard_router

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

Base.metadata.create_all(bind=engine)

SQLiteStorage.initialize()


# ============================================================
# SQLITE SCHEMA MIGRATION
# ============================================================
#
# SQLAlchemy create_all() creates missing tables but does NOT
# add new columns to an already existing table.
#
# The predictions table was originally created without:
#   - risk
#   - ai_explanation
#
# The current Prediction model requires both columns.
#
# This migration safely adds the columns when they are missing.
# ============================================================

def ensure_prediction_schema():
    """
    Ensure the predictions table contains all columns required
    by the current Prediction model.

    This is intentionally idempotent:
    - If the column already exists -> nothing happens.
    - If the column is missing -> it is added.
    """

    inspector = inspect(engine)

    if "predictions" not in inspector.get_table_names():
        logger.info(
            "Predictions table does not exist. "
            "It will be created from SQLAlchemy metadata."
        )

        Base.metadata.create_all(bind=engine)

        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("predictions")
    }

    required_columns = {
        "risk": "VARCHAR(20)",
        "ai_explanation": "TEXT",
    }

    with engine.begin() as connection:

        for column_name, column_type in required_columns.items():

            if column_name not in existing_columns:

                logger.info(
                    "Adding missing predictions column: %s",
                    column_name
                )

                connection.execute(
                    text(
                        f"""
                        ALTER TABLE predictions
                        ADD COLUMN {column_name} {column_type}
                        """
                    )
                )

                logger.info(
                    "Successfully added predictions.%s",
                    column_name
                )

            else:

                logger.info(
                    "Predictions column already exists: %s",
                    column_name
                )


# Run schema migration during application startup.
ensure_prediction_schema()


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)


# ============================================================
# MIDDLEWARE
# ============================================================

app.add_middleware(MetricsMiddleware)


# ============================================================
# API ROUTERS
# ============================================================

app.include_router(deployment_router)
app.include_router(telemetry_router)
app.include_router(predict_router)
app.include_router(signals_router)
app.include_router(feature_router)
app.include_router(regressions_router)
app.include_router(verification_router)
app.include_router(dashboard_router)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/", tags=["Application"])
def root():

    logger.info("Root endpoint accessed.")

    return {
        "application": settings.APP_NAME,
        "status": "Running",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health", tags=["Application"])
def health():

    logger.info("Health check requested.")

    return {
        "status": "Healthy"
    }


# ============================================================
# PROMETHEUS METRICS
# ============================================================

@app.get(
    "/metrics",
    include_in_schema=False
)
def metrics():

    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )