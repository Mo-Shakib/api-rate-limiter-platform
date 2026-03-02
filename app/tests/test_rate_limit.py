import time

from app.tests.helpers import seed_tenant_with_policy


def test_rate_limit_and_headers(client):
    tenant_id, api_key, _key_id = seed_tenant_with_policy(
        name=f"acme-test-{int(time.time())}", limit=5, window=60
    )

    # First 5 should be 200
    for _ in range(5):
        r = client.get("/protected/ping", headers={"X-API-Key": api_key})
        assert r.status_code == 200
        assert "X-RateLimit-Limit" in r.headers
        assert "X-RateLimit-Remaining" in r.headers
        assert "X-RateLimit-Reset" in r.headers

    # 6th should be 429, and STILL have headers
    r = client.get("/protected/ping", headers={"X-API-Key": api_key})
    assert r.status_code == 429
    assert "X-RateLimit-Limit" in r.headers
    assert "X-RateLimit-Remaining" in r.headers
    assert "X-RateLimit-Reset" in r.headers


def test_usage_increments(client):
    tenant_id, api_key, _key_id = seed_tenant_with_policy(
        name=f"usage-test-{int(time.time())}", limit=100, window=60
    )

    # Generate 3 allowed requests
    for _ in range(3):
        r = client.get("/protected/ping", headers={"X-API-Key": api_key})
        assert r.status_code == 200

    # Query last 15 minutes usage
    r = client.get(f"/usage?tenant_id={tenant_id}&last_minutes=15")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 3