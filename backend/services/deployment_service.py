from sqlalchemy.orm import Session

from backend.signals.collector import SignalCollector
from backend.normalizers.normalizer import SignalNormalizer
from backend.parsers.parser import SignalParser
from backend.storage.sqlite_storage import SQLiteStorage

from backend.monitoring.pushgateway import push_deployment_metrics
from backend.monitoring.prometheus import DEPLOYMENT_COUNT

from backend.models.telemetry import Telemetry
from backend.models.deployment import Deployment

from backend.utils.telemetry_generator import TelemetryGenerator

from backend.schemas.deployment import (
    DeploymentCreate,
    DeploymentUpdate,
)


class DeploymentService:

    @staticmethod
    def create(db: Session, deployment: DeploymentCreate):

        # -----------------------------
        # Save Deployment
        # -----------------------------
        db_deployment = Deployment(
            deployment_name=deployment.deployment_name,
            version=deployment.version,
            environment=deployment.environment,
            status=deployment.status
        )

        db.add(db_deployment)
        db.commit()
        db.refresh(db_deployment)

        # -----------------------------
        # Collect Deployment Signals
        # -----------------------------
        signal = SignalCollector.collect(
            deployment_name=db_deployment.deployment_name,
            environment=db_deployment.environment,
            status=db_deployment.status,
            source="FastAPI"
        )

        signal = SignalNormalizer.normalize(signal)
        signal = SignalParser.parse(signal)

        print("Collected Signal:", signal)

        SQLiteStorage.save(signal)

        # -----------------------------
        # Prometheus Counter
        # -----------------------------
        DEPLOYMENT_COUNT.inc()

        # -----------------------------
        # Generate Runtime Telemetry
        # -----------------------------
        telemetry = TelemetryGenerator.generate()

        db_telemetry = Telemetry(
            deployment_id=db_deployment.id,
            **telemetry
        )

        db.add(db_telemetry)
        db.commit()

        # -----------------------------
        # Push Metrics to Pushgateway
        # -----------------------------
        try:
            push_deployment_metrics(
                deployment_name=db_deployment.deployment_name,
                build_duration=12.5,
                deployment_duration=4.2,
            )
            print("✅ Metrics pushed successfully.")

        except Exception as e:
            print(f"⚠ Pushgateway Error: {e}")

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