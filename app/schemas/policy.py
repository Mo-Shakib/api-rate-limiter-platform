from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PolicyUpsert(BaseModel):
    requests_per_window: int = Field(gt=0, le=1_000_000)
    window_seconds: int = Field(gt=0, le=86_400)  # max 1 day


class PolicyOut(BaseModel):
    id: UUID
    tenant_id: UUID
    requests_per_window: int
    window_seconds: int
    created_at: datetime

    class Config:
        from_attributes = True