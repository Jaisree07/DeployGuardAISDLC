from fastapi import FastAPI
from backend.api.telemetry import router as telemetry_router
from backend.api.deployment import router as deployment_router
from backend.core.config import settings
from backend.core.logger import logger
from backend.database.database import Base, engine
from backend.models.deployment import Deployment
from backend.models.telemetry import Telemetry
from backend.api.predict import router as predict_router
from backend.models.prediction import Prediction
# Create all database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

# Register API Routers
app.include_router(deployment_router)
app.include_router(telemetry_router)
app.include_router(predict_router)

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