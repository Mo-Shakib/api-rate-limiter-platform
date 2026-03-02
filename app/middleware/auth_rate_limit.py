from app.services.usage_service import increment_usage
import time
from uuid import UUID

from fastapi import HTTPException, Request
from sqlalchemy.orm import Session

from app.core.redis import redis_client
from app.core.security import hash_api_key
from app.models.api_key import ApiKeyStatus
from app.models.policy import RateLimitPolicy
from app.models.api_key import ApiKey


def _extract_api_key(request: Request) -> str | None:
    # Option 1: Authorization: Bearer <key>
    auth = request.headers.get("authorization")
    if auth and auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip()

    # Option 2: X-API-Key: <key>
    xkey = request.headers.get("x-api-key")
    if xkey:
        return xkey.strip()

    return None


def _fixed_window_key(api_key_id: UUID, window_seconds: int, now: int) -> tuple[str, int, int]:
    window_start = (now // window_seconds) * window_seconds
    reset = window_start + window_seconds
    redis_key = f"rl:{api_key_id}:{window_start}"
    return redis_key, window_start, reset


def enforce_api_key_and_rate_limit(request: Request, db: Session) -> ApiKey:
    plaintext = _extract_api_key(request)
    if not plaintext:
        raise HTTPException(status_code=401, detail="Missing API key")

    key_hash = hash_api_key(plaintext)
    key = db.query(ApiKey).filter(ApiKey.key_hash == key_hash).one_or_none()
    if key is None or key.status != ApiKeyStatus.active:
        raise HTTPException(status_code=401, detail="Invalid or revoked API key")

    policy = db.query(RateLimitPolicy).filter(RateLimitPolicy.tenant_id == key.tenant_id).one_or_none()
    if policy is None:
        # Default policy if none set (safe fallback)
        limit = 60
        window_seconds = 60
    else:
        limit = policy.requests_per_window
        window_seconds = policy.window_seconds

    now = int(time.time())
    redis_key, _, reset = _fixed_window_key(key.id, window_seconds, now)

    # INCR + EXPIRE (fixed window)
    count = redis_client.incr(redis_key)
    if count == 1:
        redis_client.expire(redis_key, window_seconds + 1)

    remaining = max(0, limit - int(count))

    # Attach headers info so route can return them
    request.state.rate_limit = {
        "limit": limit,
        "remaining": remaining,
        "reset": reset,
    }

    if int(count) > limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    # Count usage only if request is allowed (not rate-limited)
    increment_usage(key.id)
    
    return key