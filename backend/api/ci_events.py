
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
from backend.schemas.ci_event import (
    CIEventCreate,
    CIEventResponse
)
from backend.services.ci_event_service import (
    create_ci_event,
    get_ci_events,
    get_ci_event_by_id
)


# ============================================================
# ROUTER CONFIGURATION
# ============================================================

router = APIRouter(
    prefix="/ci-events",
    tags=["CI/CD Pipeline Monitoring"]
)


# ============================================================
# GITHUB ACTIONS WEBHOOK AUTHENTICATION
# ============================================================

def verify_ci_webhook_token(
    authorization: str | None = Header(default=None)
):
    """
    Validate the Bearer token provided by GitHub Actions.

    All CI event endpoints require valid authentication.
    """

    expected_token = settings.CI_WEBHOOK_SECRET

    # Fail securely if the secret is not configured.
    if not expected_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="CI webhook authentication is not configured"
        )

    # Check whether the Authorization header is provided.
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token"
        )

    # Extract Bearer token.
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

    # Compare tokens securely using constant-time comparison.
    if not secrets.compare_digest(
        provided_token,
        expected_token
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid CI webhook token"
        )

    return True


# ============================================================
# RECEIVE CI PIPELINE EVENTS
# ============================================================

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
    """
    Receive and store an authenticated GitHub Actions event.

    GitHub Actions sends pipeline execution details to this
    endpoint after workflow execution.
    """

    return create_ci_event(db, event_data)


# ============================================================
# GET CI PIPELINE HISTORY
# ============================================================

@router.get(
    "/",
    response_model=list[CIEventResponse]
)
def list_ci_events(
    limit: int = Query(
        default=50,
        ge=1,
        le=200
    ),
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_ci_webhook_token)
):
    """
    Retrieve recent GitHub Actions pipeline events.

    Requires Bearer token authentication.
    """

    return get_ci_events(db, limit)


# ============================================================
# GET CI EVENT BY ID
# ============================================================

@router.get(
    "/{event_id}",
    response_model=CIEventResponse
)
def retrieve_ci_event(
    event_id: int,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_ci_webhook_token)
):
    """
    Retrieve a specific GitHub Actions pipeline event.

    Requires Bearer token authentication.
    """

    event = get_ci_event_by_id(db, event_id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CI event not found"
        )

    return event
