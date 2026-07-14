from fastapi import FastAPI
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
from backend.models.prediction import Prediction
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from backend.middleware.metrics import MetricsMiddleware
# Create all database tables
Base.metadata.create_all(bind=engine)
SQLiteStorage.initialize()
# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

# Register API Routers
app.add_middleware(MetricsMiddleware)
app.include_router(deployment_router)
app.include_router(telemetry_router)
app.include_router(predict_router)
app.include_router(signals_router)
app.include_router(feature_router)
app.include_router(regressions_router)

@app.get("/", tags=["Application"])
def root():
    """
    Root endpoint to verify the application is running.
    """
    logger.info("Root endpoint accessed.")

    return {
        "application": settings.APP_NAME,
        "status": "Running",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/health", tags=["Application"])
def health():
    """
    Health check endpoint.
    """
    logger.info("Health check requested.")

    return {
        "status": "Healthy"
    }

@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )