from sqlalchemy.orm import Session

from app.models.tenant import Tenant


def create_tenant(db: Session, name: str) -> Tenant:
    tenant = Tenant(name=name)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


def list_tenants(db: Session) -> list[Tenant]:
    return db.query(Tenant).order_by(Tenant.created_at.desc()).all()