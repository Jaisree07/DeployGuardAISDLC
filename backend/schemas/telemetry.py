from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TelemetryCreate(BaseModel):
    deployment_id: int
    cpu_usage: float
    memory_usage: float
    latency: float
    build_duration: float
    deployment_duration: float
    error_count: int


class TelemetryResponse(BaseModel):

    id: int
    deployment_id: int
    cpu_usage: float
    memory_usage: float
    latency: float
    build_duration: float
    deployment_duration: float
    error_count: int
    collected_at: datetime

    model_config = ConfigDict(from_attributes=True)