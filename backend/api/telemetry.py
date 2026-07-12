from typing import List

from fastapi import APIRouter, Depends
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