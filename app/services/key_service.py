from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.security import api_key_prefix, generate_api_key, hash_api_key
from app.models.api_key import ApiKey, ApiKeyStatus
from app.models.tenant import Tenant


def create_key(db: Session, tenant_id: UUID, name: str | None = None) -> tuple[str, ApiKey]:
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).one_or_none()
    if tenant is None:
        raise ValueError("TENANT_NOT_FOUND")

    plaintext = generate_api_key()
    key = ApiKey(
        tenant_id=tenant_id,
        key_prefix=api_key_prefix(plaintext),
        key_hash=hash_api_key(plaintext),
        name=name,
        status=ApiKeyStatus.active,
    )
    db.add(key)
    db.commit()
    db.refresh(key)
    return plaintext, key


def list_keys(db: Session, tenant_id: UUID) -> list[ApiKey]:
    return (
        db.query(ApiKey)
        .filter(ApiKey.tenant_id == tenant_id)
        .order_by(ApiKey.created_at.desc())
        .all()
    )


def revoke_key(db: Session, key_id: UUID) -> ApiKey:
    key = db.query(ApiKey).filter(ApiKey.id == key_id).one_or_none()
    if key is None:
        raise ValueError("KEY_NOT_FOUND")

    if key.status != ApiKeyStatus.revoked:
        key.status = ApiKeyStatus.revoked
        key.revoked_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(key)

    return key


def rotate_key(db: Session, key_id: UUID) -> tuple[str, ApiKey]:
    old = db.query(ApiKey).filter(ApiKey.id == key_id).one_or_none()
    if old is None:
        raise ValueError("KEY_NOT_FOUND")

    tenant_id = old.tenant_id
    revoke_key(db, key_id)  # revoke old

    plaintext, new_key = create_key(db, tenant_id=tenant_id, name=(old.name or "rotated"))
    return plaintext, new_key