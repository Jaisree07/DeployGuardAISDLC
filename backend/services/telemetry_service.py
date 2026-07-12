from sqlalchemy.orm import Session

from backend.models.telemetry import Telemetry
from backend.schemas.telemetry import TelemetryCreate


class TelemetryService:

    @staticmethod
    def create(db: Session, telemetry: TelemetryCreate):

        obj = Telemetry(**telemetry.model_dump())

        db.add(obj)

        db.commit()

        db.refresh(obj)

        return obj

    @staticmethod
    def get_all(db: Session):

        return db.query(Telemetry).all()