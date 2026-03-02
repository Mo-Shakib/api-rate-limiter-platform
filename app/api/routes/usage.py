from datetime import datetime, timezone, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.redis import redis_client
from app.models.api_key import ApiKey
from app.models.tenant import Tenant
from app.services.usage_service import iter_minute_buckets

router = APIRouter(prefix="/usage", tags=["usage"])


def _parse_dt(s: str) -> datetime:
    # Accept ISO strings like 2026-03-02T04:00:00Z or without Z
    # Convert to UTC-aware datetime
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


@router.get("")
def usage_report(
    tenant_id: UUID = Query(...),
    start: str | None = Query(None, description="ISO datetime, e.g. 2026-03-02T04:00:00Z"),
    end: str | None = Query(None, description="ISO datetime, e.g. 2026-03-02T04:10:00Z"),
    last_minutes: int | None = Query(
        None, ge=1, le=24 * 60, description="If provided, ignores start/end and returns last N minutes"
    ),
    db: Session = Depends(get_db),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).one_or_none()
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    now = datetime.now(timezone.utc)

    if last_minutes is not None:
        end_dt = now
        start_dt = now - timedelta(minutes=last_minutes)
    else:
        if start is None or end is None:
            raise HTTPException(status_code=400, detail="Provide start and end, or use last_minutes")
        start_dt = _parse_dt(start)
        end_dt = _parse_dt(end)

    if end_dt < start_dt:
        raise HTTPException(status_code=400, detail="end must be >= start")

    keys = db.query(ApiKey).filter(ApiKey.tenant_id == tenant_id).all()
    key_ids = [k.id for k in keys]

    # Build all redis keys for the time range
    minute_buckets = list(iter_minute_buckets(start_dt, end_dt))

    # For each minute bucket, sum usage across all keys
    points = []
    total = 0

    for b in minute_buckets:
        redis_keys = [f"usage:{kid}:{b.strftime('%Y%m%d%H%M')}" for kid in key_ids]
        counts = []
        if redis_keys:
            counts = redis_client.mget(redis_keys)

        minute_sum = sum(int(c) for c in counts if c is not None)
        total += minute_sum

        points.append(
            {
                "ts": b.isoformat().replace("+00:00", "Z"),
                "count": minute_sum,
            }
        )

    return {
        "tenant_id": str(tenant_id),
        "start": start_dt.isoformat().replace("+00:00", "Z"),
        "end": end_dt.isoformat().replace("+00:00", "Z"),
        "total": total,
        "points": points,
    }