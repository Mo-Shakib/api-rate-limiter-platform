from sqlalchemy.orm import Session

from app.models.policy import RateLimitPolicy


def upsert_policy(
    db: Session, tenant_id, requests_per_window: int, window_seconds: int
) -> RateLimitPolicy:
    policy = db.query(RateLimitPolicy).filter(RateLimitPolicy.tenant_id == tenant_id).one_or_none()

    if policy is None:
        policy = RateLimitPolicy(
            tenant_id=tenant_id,
            requests_per_window=requests_per_window,
            window_seconds=window_seconds,
        )
        db.add(policy)
    else:
        policy.requests_per_window = requests_per_window
        policy.window_seconds = window_seconds

    db.commit()
    db.refresh(policy)
    return policy


def get_policy(db: Session, tenant_id) -> RateLimitPolicy | None:
    return db.query(RateLimitPolicy).filter(RateLimitPolicy.tenant_id == tenant_id).one_or_none()