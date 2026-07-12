from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DeploymentCreate(BaseModel):
    deployment_name: str
    version: str
    environment: str
    status: str


class DeploymentUpdate(BaseModel):
    deployment_name: str
    version: str
    environment: str
    status: str


class DeploymentResponse(BaseModel):
    id: int
    deployment_name: str
    version: str
    environment: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)