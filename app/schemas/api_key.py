from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ApiKeyCreate(BaseModel):
    name: str | None = Field(default=None, max_length=120)


class ApiKeyOut(BaseModel):
    id: UUID
    tenant_id: UUID
    key_prefix: str
    name: str | None
    status: str
    created_at: datetime
    revoked_at: datetime | None

    class Config:
        from_attributes = True


class ApiKeyCreatedResponse(BaseModel):
    api_key: str  # plaintext, returned once
    key: ApiKeyOut