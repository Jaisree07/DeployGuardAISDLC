from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship

from backend.database.database import Base


class Prediction(Base):

    __tablename__ = "predictions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    deployment_id = Column(
        Integer,
        ForeignKey("deployments.id"),
        nullable=False
    )

    prediction = Column(
        String(50)
    )

    confidence = Column(
        Float
    )

    anomaly = Column(
        String(20)
    )

    risk = Column(
        String(20)
    )

    ai_explanation = Column(
        Text
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    deployment = relationship(
        "Deployment"
    )