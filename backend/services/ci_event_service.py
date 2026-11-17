
from sqlalchemy.orm import Session

from backend.models.ci_event import CIEvent
from backend.schemas.ci_event import CIEventCreate
from backend.monitoring.prometheus import (
    CI_PIPELINE_RUNS,
    CI_PIPELINE_DURATION,
)


def create_ci_event(
    db: Session,
    event_data: CIEventCreate
) -> CIEvent:
    """
    Create or update a GitHub Actions pipeline event.

    A pipeline execution is uniquely identified by:
    repository + run_id + run_attempt.

    Prometheus metrics are updated only when the execution
    reaches completed status for the first time.
    """

    event_values = event_data.model_dump()

    existing_event = (
        db.query(CIEvent)
        .filter(
            CIEvent.repository == event_data.repository,
            CIEvent.run_id == event_data.run_id,
            CIEvent.run_attempt == event_data.run_attempt,
        )
        .first()
    )

    # Ignore stale status updates arriving after completion.
    if existing_event and existing_event.status == "completed":
        if event_data.status != "completed":
            return existing_event

    is_first_completion = (
        event_data.status == "completed"
        and (
            existing_event is None
            or existing_event.status != "completed"
        )
    )

    try:
        if existing_event:
            for field, value in event_values.items():
                setattr(existing_event, field, value)

            ci_event = existing_event

        else:
            ci_event = CIEvent(**event_values)
            db.add(ci_event)

        db.commit()
        db.refresh(ci_event)

    except Exception:
        db.rollback()
        raise

    # Update Prometheus only after the database commit succeeds.
    if is_first_completion:
        outcome = event_data.conclusion or "unknown"

        CI_PIPELINE_RUNS.labels(
            workflow=event_data.workflow_name,
            status=outcome,
        ).inc()

        if event_data.duration_seconds is not None:
            CI_PIPELINE_DURATION.labels(
                workflow=event_data.workflow_name
            ).observe(event_data.duration_seconds)

    return ci_event


def get_ci_events(
    db: Session,
    limit: int = 50
):
    """Retrieve recent GitHub Actions pipeline events."""

    return (
        db.query(CIEvent)
        .order_by(CIEvent.created_at.desc())
        .limit(limit)
        .all()
    )


def get_ci_event_by_id(
    db: Session,
    event_id: int
):
    """Retrieve a specific CI event by database ID."""

    return (
        db.query(CIEvent)
        .filter(CIEvent.id == event_id)
        .first()
    )
