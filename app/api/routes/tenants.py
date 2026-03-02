from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.tenant import TenantCreate, TenantOut
from app.services.tenant_service import create_tenant, list_tenants

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.post("", response_model=TenantOut, status_code=status.HTTP_201_CREATED)
def create_tenant_endpoint(payload: TenantCreate, db: Session = Depends(get_db)):
    try:
        return create_tenant(db, payload.name)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tenant name already exists",
        )


@router.get("", response_model=list[TenantOut])
def list_tenants_endpoint(db: Session = Depends(get_db)):
    return list_tenants(db)