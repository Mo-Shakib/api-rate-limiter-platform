from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.api_key import ApiKeyCreate, ApiKeyCreatedResponse, ApiKeyOut
from app.services.key_service import create_key, list_keys, revoke_key, rotate_key

router = APIRouter(tags=["keys"])


@router.post(
    "/tenants/{tenant_id}/keys",
    response_model=ApiKeyCreatedResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_key_endpoint(
    tenant_id: UUID, payload: ApiKeyCreate, db: Session = Depends(get_db)
):
    try:
        plaintext, key = create_key(db, tenant_id=tenant_id, name=payload.name)
        return {"api_key": plaintext, "key": key}
    except ValueError as e:
        if str(e) == "TENANT_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Tenant not found")
        raise


@router.get("/tenants/{tenant_id}/keys", response_model=list[ApiKeyOut])
def list_keys_endpoint(tenant_id: UUID, db: Session = Depends(get_db)):
    return list_keys(db, tenant_id)


@router.post("/keys/{key_id}/revoke", response_model=ApiKeyOut)
def revoke_key_endpoint(key_id: UUID, db: Session = Depends(get_db)):
    try:
        return revoke_key(db, key_id)
    except ValueError as e:
        if str(e) == "KEY_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Key not found")
        raise


@router.post("/keys/{key_id}/rotate", response_model=ApiKeyCreatedResponse)
def rotate_key_endpoint(key_id: UUID, db: Session = Depends(get_db)):
    try:
        plaintext, key = rotate_key(db, key_id)
        return {"api_key": plaintext, "key": key}
    except ValueError as e:
        if str(e) == "KEY_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Key not found")
        raise