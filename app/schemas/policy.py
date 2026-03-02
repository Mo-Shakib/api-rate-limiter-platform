from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class PolicyUpsert(BaseModel):
    requests_per_window: int = Field(gt=0, le=1_000_000)
    window_seconds: int = Field(gt=0, le=86_400)


class PolicyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    requests_per_window: int
    window_seconds: int
    created_at: datetime