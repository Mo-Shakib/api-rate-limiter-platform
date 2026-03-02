from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class TenantCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)


class TenantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    created_at: datetime