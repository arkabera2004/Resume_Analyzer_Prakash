"""Verifies rate limiting actually triggers — every other test file runs with
the limiter disabled (see conftest.py) since httpx's ASGITransport gives every
request the same fake client IP, which would otherwise collide across tests.
This file deliberately re-enables it and resets the counter first/after.
"""
import pytest

from app.utils.rate_limit import limiter


@pytest.fixture(autouse=True)
def _enable_rate_limiting():
    limiter.reset()
    limiter.enabled = True
    yield
    limiter.enabled = False
    limiter.reset()


async def test_login_is_rate_limited_after_repeated_requests(async_client):
    # login's limit is 10/minute; a wrong-password login still counts against
    # it since the limiter runs before the handler's own 401 logic.
    payload = {"email": "nobody@example.com", "password": "wrongpassword"}

    statuses = []
    for _ in range(12):
        response = await async_client.post("/api/auth/login", json=payload)
        statuses.append(response.status_code)

    assert 429 in statuses
    # Everything before the limit kicks in should be the normal 401 (bad creds),
    # not some other failure mode.
    first_hit_index = statuses.index(429)
    assert all(status == 401 for status in statuses[:first_hit_index])


async def test_register_is_rate_limited_after_repeated_requests(async_client):
    # register's limit is 5/minute.
    statuses = []
    for i in range(7):
        response = await async_client.post(
            "/api/auth/register",
            json={"name": "Spammer", "email": f"spammer{i}@example.com", "password": "supersecret123"},
        )
        statuses.append(response.status_code)

    assert 429 in statuses
