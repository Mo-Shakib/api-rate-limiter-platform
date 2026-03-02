from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.tenant_service import create_tenant
from app.services.policy_service import upsert_policy
from app.services.key_service import create_key


def seed_tenant_with_policy(name: str = "test-tenant", limit: int = 5, window: int = 60):
    db: Session = SessionLocal()
    try:
        tenant = create_tenant(db, name=name)
        upsert_policy(db, tenant.id, limit, window)
        plaintext, key = create_key(db, tenant.id, name="test-key")

        # Return primitives (safe after session closes)
        return str(tenant.id), plaintext, str(key.id)
    finally:
        db.close()