
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Float

from backend.database.database import Base


class CIEvent(Base):
    __tablename__ = "ci_events"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    repository = Column(
        String(200),
        nullable=False
    )

    workflow_name = Column(
        String(200),
        nullable=False
    )

    run_id = Column(
        String(100),
        nullable=False,
        index=True
    )

    run_attempt = Column(
        Integer,
        nullable=False,
        default=1
    )

    branch = Column(
        String(200),
        nullable=True
    )

    commit_sha = Column(
        String(100),
        nullable=True
    )

    event_name = Column(
        String(100),
        nullable=True
    )

    status = Column(
        String(30),
        nullable=False
    )

    conclusion = Column(
        String(30),
        nullable=True
    )

    started_at = Column(
        DateTime,
        nullable=True
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )

    duration_seconds = Column(
        Float,
        nullable=True
    )

    html_url = Column(
        String(500),
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
