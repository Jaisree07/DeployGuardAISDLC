from pydantic import BaseModel


class PredictionRequest(BaseModel):

    environment: str

    cpu_usage: float

    memory_usage: float

    latency: float

    build_duration: float

    deployment_duration: float

    error_count: int