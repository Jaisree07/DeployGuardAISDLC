from datetime import datetime

from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from backend.database.database import Base


class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)

    deployment_id = Column(
        Integer,
        ForeignKey("deployments.id"),
        nullable=False
    )

    deployment = relationship(
        "Deployment",
        back_populates="telemetry"
    )

    cpu_usage = Column(Float)

    memory_usage = Column(Float)

    latency = Column(Float)

    build_duration = Column(Float)

    deployment_duration = Column(Float)

    error_count = Column(Integer)

    collected_at = Column(
        DateTime,
        default=datetime.utcnow
    )