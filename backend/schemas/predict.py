from pydantic import BaseModel


class PredictionRequest(BaseModel):

    cpu_usage: float

    memory_usage: float

    latency: float

    build_duration: float

    deployment_duration: float

    error_count: int

    resource_usage: float

    deployment_speed: float

    failure_risk: float