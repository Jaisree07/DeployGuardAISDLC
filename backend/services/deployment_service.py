from sqlalchemy.orm import Session

from backend.models.telemetry import Telemetry
from backend.utils.telemetry_generator import TelemetryGenerator
from backend.models.deployment import Deployment
from backend.schemas.deployment import (
    DeploymentCreate,
    DeploymentUpdate,
)


class DeploymentService:

    @staticmethod
    def create(db: Session, deployment: DeploymentCreate):

        db_deployment = Deployment(
            deployment_name=deployment.deployment_name,
            version=deployment.version,
            environment=deployment.environment,
            status=deployment.status
        )

        db.add(db_deployment)
        db.commit()
        db.refresh(db_deployment)

        telemetry = TelemetryGenerator.generate()

        db_telemetry = Telemetry(
            deployment_id=db_deployment.id,
            **telemetry
        )

        db.add(db_telemetry)
        db.commit()

        return db_deployment

    @staticmethod
    def get_all(db: Session):

        return db.query(Deployment).all()

    @staticmethod
    def get_by_id(db: Session, deployment_id: int):

        return (
            db.query(Deployment)
            .filter(Deployment.id == deployment_id)
            .first()
        )

    @staticmethod
    def update(
        db: Session,
        deployment_id: int,
        deployment: DeploymentUpdate
    ):

        db_deployment = (
            db.query(Deployment)
            .filter(Deployment.id == deployment_id)
            .first()
        )

        if not db_deployment:
            return None

        db_deployment.deployment_name = deployment.deployment_name
        db_deployment.version = deployment.version
        db_deployment.environment = deployment.environment
        db_deployment.status = deployment.status

        db.commit()
        db.refresh(db_deployment)

        return db_deployment

    @staticmethod
    def delete(db: Session, deployment_id: int):

        db_deployment = (
            db.query(Deployment)
            .filter(Deployment.id == deployment_id)
            .first()
        )

        if not db_deployment:
            return None

        db.delete(db_deployment)
        db.commit()

        return db_deployment