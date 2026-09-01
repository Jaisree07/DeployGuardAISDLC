from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas.telemetry import (
    TelemetryCreate,
    TelemetryResponse,
)
from backend.services.telemetry_service import TelemetryService


router = APIRouter(
    prefix="/telemetry",
    tags=["Telemetry"]
)


@router.post("/", response_model=TelemetryResponse)
def create_telemetry(
    telemetry: TelemetryCreate,
    db: Session = Depends(get_db)
):

    return TelemetryService.create(db, telemetry)


@router.get("/", response_model=List[TelemetryResponse])
def get_all_telemetry(
    db: Session = Depends(get_db)
):

    return TelemetryService.get_all(db)


@router.get(
    "/{deployment_id}",
    response_model=TelemetryResponse
)
def get_telemetry_by_deployment(
    deployment_id: int,
    db: Session = Depends(get_db)
):

    telemetry = TelemetryService.get_by_deployment_id(
        db,
        deployment_id
    )

    if telemetry is None:
        raise HTTPException(
            status_code=404,
            detail="Telemetry not found for deployment"
        )

    return telemetry