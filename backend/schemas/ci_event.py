
from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CIEventCreate(BaseModel):

    repository: str = Field(
        ...,
        min_length=1,
        max_length=200
    )

    workflow_name: str = Field(
        ...,
        min_length=1,
        max_length=200
    )

    run_id: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    run_attempt: int = Field(
        default=1,
        ge=1
    )

    branch: Optional[str] = Field(
        default=None,
        max_length=200
    )

    commit_sha: Optional[str] = Field(
        default=None,
        max_length=100
    )

    event_name: Optional[str] = Field(
        default=None,
        max_length=100
    )

    status: Literal[
        "queued",
        "in_progress",
        "completed"
    ]

    conclusion: Optional[Literal[
        "success",
        "failure",
        "cancelled",
        "skipped",
        "timed_out",
        "action_required",
        "neutral"
    ]] = None

    started_at: Optional[datetime] = None

    completed_at: Optional[datetime] = None

    duration_seconds: Optional[float] = Field(
        default=None,
        ge=0
    )

    html_url: Optional[str] = Field(
        default=None,
        max_length=500
    )

    @model_validator(mode="after")
    def validate_completion(self):

        if self.status == "completed" and self.conclusion is None:
            raise ValueError(
                "Conclusion is required when status is completed"
            )

        if self.status != "completed" and self.conclusion is not None:
            raise ValueError(
                "Conclusion must be empty unless status is completed"
            )

        return self


class CIEventResponse(BaseModel):

    id: int

    repository: str

    workflow_name: str

    run_id: str

    run_attempt: int

    branch: Optional[str]

    commit_sha: Optional[str]

    event_name: Optional[str]

    status: str

    conclusion: Optional[str]

    started_at: Optional[datetime]

    completed_at: Optional[datetime]

    duration_seconds: Optional[float]

    html_url: Optional[str]

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
