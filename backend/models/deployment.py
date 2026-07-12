from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from backend.database.database import Base


class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True)

    deployment_name = Column(String(100), nullable=False)

    version = Column(String(20), nullable=False)

    environment = Column(String(20), nullable=False)

    status = Column(String(20), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    telemetry = relationship(
        "Telemetry",
        back_populates="deployment",
        cascade="all, delete-orphan"
    )