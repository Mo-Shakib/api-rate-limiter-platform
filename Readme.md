# API Rate Limiter + Key Management Platform (MVP)

A small "control plane + gateway" style service:
- Control plane: create tenants, set rate limit policy, issue/revoke/rotate API keys
- Gateway enforcement: validate API keys, enforce Redis-backed rate limits, return standard headers
- Usage tracking: per-minute Redis counters + usage report endpoint

## Features
- Tenants
  - Create tenant
  - List tenants
- Rate Limit Policy (per tenant)
  - Set policy: `requests_per_window`, `window_seconds`
  - Get policy
- API Keys (per tenant)
  - Create API key (plaintext returned **once**)
  - List keys (no plaintext)
  - Revoke key
  - Rotate key (revokes old, returns new plaintext once)
- Rate Limiting (Redis fixed window)
  - 401 when missing/invalid key
  - 429 when exceeded
  - `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` headers on **200 and 429**
- Usage tracking (Redis per-minute buckets)
  - `/usage?tenant_id=...&start=...&end=...`
  - `/usage?tenant_id=...&last_minutes=15`

## Tech Stack
- FastAPI + SQLAlchemy + Alembic
- Postgres (tenants/keys/policies)
- Redis (rate limit counters + usage counters)
- Pytest integration tests
- GitHub Actions CI (lint + migrations + tests)

## Architecture
- Postgres holds long-lived data: tenants, api keys (hashed), rate policies
- Redis holds short-lived counters:
  - Rate limit key: `rl:{api_key_id}:{window_start_epoch}`
  - Usage key: `usage:{api_key_id}:{YYYYMMDDHHMM}`

Rate limiting algorithm: **fixed window counter**
- `INCR` on a window key
- `EXPIRE` to window length (+1 sec)
- If count > limit → 429

## Local Setup

### 1) Configure env
```bash
cp .env.example .env
```

### **2) Start Postgres + Redis**

```
docker compose up -d
docker compose ps
```



### **3) Install deps (macOS / Linux)**

```
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
```



### **4) Run migrations**

```
alembic upgrade head
```

### **5) Run the API**


```
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open:

- http://localhost:8000/docs


## **API Usage (Curl)**


### **Create Tenant**


```
curl -s -X POST "http://localhost:8000/tenants" \
  -H "Content-Type: application/json" \
  -d '{"name":"acme"}' | python -m json.tool
```

### **Set Policy (5 requests per 60 seconds)**

```
curl -s -X PUT "http://localhost:8000/tenants/<TENANT_ID>/policy" \
  -H "Content-Type: application/json" \
  -d '{"requests_per_window": 5, "window_seconds": 60}' | python -m json.tool
```

### **Create API Key (plaintext returned once)**

```
curl -s -X POST "http://localhost:8000/tenants/<TENANT_ID>/keys" \
  -H "Content-Type: application/json" \
  -d '{"name":"acme-dev"}' | python -m json.tool
```

Save the returned api_key.

### **Call Protected Endpoint**

```
curl -i "http://localhost:8000/protected/ping" \
  -H "X-API-Key: <API_KEY>"
```

### **Trigger 429 (policy=5/min)**

```
for i in {1..6}; do
  echo "---- $i"
  curl -s -o /dev/null -w "%{http_code}\n" \
    "http://localhost:8000/protected/ping" \
    -H "X-API-Key: <API_KEY>"
done
```

### **Usage Report (last 15 minutes)**

```
curl -s "http://localhost:8000/usage?tenant_id=<TENANT_ID>&last_minutes=15" | python -m json.tool
```
## **Tests**

Make sure docker services are up, then:

```
pytest -q
```
