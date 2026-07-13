from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas.deployment import (
    DeploymentCreate,
    DeploymentUpdate,
    DeploymentResponse,
)
from backend.services.deployment_service import DeploymentService

from backend.monitoring.prometheus import (
    DEPLOYMENT_COUNT,
    DEPLOYMENT_SUCCESS,
    DEPLOYMENT_FAILURE,
)

router = APIRouter(prefix="/deployments", tags=["Deployments"])


@router.post("/", response_model=DeploymentResponse)
def create_deployment(
    deployment: DeploymentCreate,
    db: Session = Depends(get_db)
):
    try:
        result = DeploymentService.create(db, deployment)

        DEPLOYMENT_COUNT.inc()
        DEPLOYMENT_SUCCESS.inc()

        return result

    except Exception:
        DEPLOYMENT_FAILURE.inc()
        raise


@router.get("/", response_model=List[DeploymentResponse])
def get_deployments(db: Session = Depends(get_db)):
    return DeploymentService.get_all(db)


@router.get("/{deployment_id}", response_model=DeploymentResponse)
def get_deployment(
    deployment_id: int,
    db: Session = Depends(get_db)
):
    deployment = DeploymentService.get_by_id(db, deployment_id)

    if deployment is None:
        raise HTTPException(status_code=404, detail="Deployment not found")

    return deployment


@router.put("/{deployment_id}", response_model=DeploymentResponse)
def update_deployment(
    deployment_id: int,
    deployment: DeploymentUpdate,
    db: Session = Depends(get_db)
):
    updated = DeploymentService.update(db, deployment_id, deployment)

    if updated is None:
        raise HTTPException(status_code=404, detail="Deployment not found")

    return updated


@router.delete("/{deployment_id}")
def delete_deployment(
    deployment_id: int,
    db: Session = Depends(get_db)
):
    deleted = DeploymentService.delete(db, deployment_id)

    if deleted is None:
        raise HTTPException(status_code=404, detail="Deployment not found")

    return {"message": "Deployment deleted successfully"}