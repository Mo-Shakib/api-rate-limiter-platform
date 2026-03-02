from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.core.redis import redis_client


def _bucket_minute(dt: datetime) -> datetime:
    # normalize to UTC minute boundary
    dt = dt.astimezone(timezone.utc)
    return dt.replace(second=0, microsecond=0)


def _bucket_key(api_key_id: UUID, dt: datetime) -> str:
    # usage:<key_id>:YYYYMMDDHHMM
    stamp = dt.strftime("%Y%m%d%H%M")
    return f"usage:{api_key_id}:{stamp}"


def increment_usage(api_key_id: UUID, now: datetime | None = None, retention_days: int = 7) -> None:
    now = now or datetime.now(timezone.utc)
    bucket = _bucket_minute(now)
    key = _bucket_key(api_key_id, bucket)

    redis_client.incr(key)

    # keep a little longer than retention window
    ttl = int(timedelta(days=retention_days).total_seconds()) + 3600
    redis_client.expire(key, ttl)


def iter_minute_buckets(start: datetime, end: datetime):
    # inclusive start minute -> inclusive end minute
    cur = _bucket_minute(start)
    endb = _bucket_minute(end)
    while cur <= endb:
        yield cur
        cur += timedelta(minutes=1)