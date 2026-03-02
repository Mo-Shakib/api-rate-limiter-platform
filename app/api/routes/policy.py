from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.tenant import Tenant
from app.schemas.policy import PolicyOut, PolicyUpsert
from app.services.policy_service import get_policy, upsert_policy

router = APIRouter(prefix="/tenants/{tenant_id}/policy", tags=["policy"])


@router.put("", response_model=PolicyOut)
def upsert_policy_endpoint(tenant_id: str, payload: PolicyUpsert, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).one_or_none()
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return upsert_policy(db, tenant_id, payload.requests_per_window, payload.window_seconds)


@router.get("", response_model=PolicyOut)
def get_policy_endpoint(tenant_id: str, db: Session = Depends(get_db)):
    policy = get_policy(db, tenant_id)
    if policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy