from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.services.verification_service import VerificationService


router = APIRouter(
    prefix="/verification",
    tags=["Verification"]
)


@router.post("/{deployment_id}")
def verify_deployment(
    deployment_id: int,
    db: Session = Depends(get_db)
):
    try:
        result = VerificationService.verify(
            db=db,
            deployment_id=deployment_id
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Deployment verification failed: {str(e)}"
        )
