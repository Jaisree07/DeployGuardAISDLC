
import secrets

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Query,
    status
)
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.database.database import get_db
from backend.schemas.ci_event import CIEventCreate, CIEventResponse

from backend.services.ci_event_service import (
    create_ci_event,
    get_ci_events,
    get_ci_event_by_id
)

from backend.services.ci_insights_service import (
    generate_ci_pipeline_insights
)


router = APIRouter(
    prefix="/ci-events",
    tags=["CI/CD Pipeline Monitoring"]
)


# --------------------------------------------------
# GitHub Actions Authentication
# --------------------------------------------------

def verify_ci_webhook_token(
    authorization: str | None = Header(default=None)
):
    expected_token = settings.CI_WEBHOOK_SECRET

    if not expected_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="CI webhook authentication is not configured"
        )

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token"
        )

    scheme, separator, provided_token = authorization.partition(" ")

    if (
        not separator
        or scheme.lower() != "bearer"
        or not provided_token
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format"
        )

    if not secrets.compare_digest(provided_token, expected_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid CI webhook token"
        )

    return True


# --------------------------------------------------
# Grafana Read-Only Authentication
# --------------------------------------------------

def verify_grafana_token(
    authorization: str | None = Header(default=None)
):
    expected_token = settings.GRAFANA_API_TOKEN

    if not expected_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Grafana API authentication is not configured"
        )

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Grafana authorization token"
        )

    scheme, separator, provided_token = authorization.partition(" ")

    if (
        not separator
        or scheme.lower() != "bearer"
        or not provided_token
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Grafana authorization format"
        )

    if not secrets.compare_digest(provided_token, expected_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Grafana API token"
        )

    return True


# --------------------------------------------------
# Receive CI Event - GitHub Actions
# --------------------------------------------------

@router.post(
    "/",
    response_model=CIEventResponse,
    status_code=status.HTTP_201_CREATED
)
def receive_ci_event(
    event_data: CIEventCreate,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_ci_webhook_token)
):
    return create_ci_event(db, event_data)


# --------------------------------------------------
# List CI Events - GitHub Actions Authentication
# --------------------------------------------------

@router.get(
    "/",
    response_model=list[CIEventResponse]
)
def list_ci_events(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_ci_webhook_token)
):
    return get_ci_events(db, limit)


# --------------------------------------------------
# AI Pipeline Insights - Grafana Authentication
# --------------------------------------------------

@router.get("/ai-insights")
def get_ci_ai_insights(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_grafana_token)
):
    return generate_ci_pipeline_insights(db, limit)


# --------------------------------------------------
# Retrieve Individual CI Event
# --------------------------------------------------

@router.get(
    "/{event_id}",
    response_model=CIEventResponse
)
def retrieve_ci_event(
    event_id: int,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_ci_webhook_token)
):
    event = get_ci_event_by_id(db, event_id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CI event not found"
        )

    return event
