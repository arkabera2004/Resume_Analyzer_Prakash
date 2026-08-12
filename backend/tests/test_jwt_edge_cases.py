"""Deliberately adversarial JWT tests — expired, tampered, forged, and deleted-user
tokens all must be rejected the same way a garbage string is, per get_current_user's
security guarantee (see app/utils/deps.py)."""
from datetime import datetime, timedelta, timezone

import pytest
from bson import ObjectId
from jose import jwt

from app.config import get_settings
from app.database import get_users_collection

settings = get_settings()


@pytest.fixture
def user_payload():
    return {"name": "JWT Test User", "email": "jwtuser@example.com", "password": "supersecret123"}


def _make_token(sub: str | None, secret: str, algorithm: str, expires_in: timedelta) -> str:
    payload = {"exp": datetime.now(timezone.utc) + expires_in}
    if sub is not None:
        payload["sub"] = sub
    return jwt.encode(payload, secret, algorithm=algorithm)


async def test_expired_token_is_rejected(async_client, user_payload):
    register_response = await async_client.post("/api/auth/register", json=user_payload)
    user_id = register_response.json()["user"]["id"]

    expired_token = _make_token(
        sub=user_id, secret=settings.jwt_secret, algorithm=settings.jwt_algorithm,
        expires_in=timedelta(minutes=-1),
    )

    response = await async_client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401


async def test_token_signed_with_wrong_secret_is_rejected(async_client, user_payload):
    register_response = await async_client.post("/api/auth/register", json=user_payload)
    user_id = register_response.json()["user"]["id"]

    forged_token = _make_token(
        sub=user_id, secret="a-completely-different-secret", algorithm=settings.jwt_algorithm,
        expires_in=timedelta(minutes=30),
    )

    response = await async_client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {forged_token}"}
    )
    assert response.status_code == 401


async def test_tampered_token_signature_is_rejected(async_client, user_payload):
    register_response = await async_client.post("/api/auth/register", json=user_payload)
    valid_token = register_response.json()["access_token"]

    # Flip the last character of the signature segment.
    header, payload, signature = valid_token.rsplit(".", 2)
    tampered_char = "a" if signature[-1] != "a" else "b"
    tampered_token = f"{header}.{payload}.{signature[:-1]}{tampered_char}"

    response = await async_client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {tampered_token}"}
    )
    assert response.status_code == 401


async def test_token_missing_subject_claim_is_rejected(async_client):
    token_without_sub = _make_token(
        sub=None, secret=settings.jwt_secret, algorithm=settings.jwt_algorithm,
        expires_in=timedelta(minutes=30),
    )

    response = await async_client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {token_without_sub}"}
    )
    assert response.status_code == 401


async def test_token_with_malformed_subject_is_rejected(async_client):
    # "sub" isn't a valid ObjectId hex string.
    token = _make_token(
        sub="not-an-object-id", secret=settings.jwt_secret, algorithm=settings.jwt_algorithm,
        expires_in=timedelta(minutes=30),
    )

    response = await async_client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


async def test_token_for_deleted_user_is_rejected(async_client, user_payload):
    register_response = await async_client.post("/api/auth/register", json=user_payload)
    token = register_response.json()["access_token"]
    user_id = register_response.json()["user"]["id"]

    users = get_users_collection()
    await users.delete_one({"_id": ObjectId(user_id)})

    response = await async_client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


async def test_token_with_none_algorithm_is_rejected(async_client, user_payload):
    """The classic 'alg: none' JWT forgery attempt — a token with no signature at
    all must not be accepted just because it has a well-formed payload.

    python-jose refuses to even encode an 'alg: none' token (confirms the library
    doesn't support that attack surface at all), so the forged token has to be
    hand-assembled the way a real attacker — not using this library — would.
    """
    import base64
    import json

    register_response = await async_client.post("/api/auth/register", json=user_payload)
    user_id = register_response.json()["user"]["id"]

    def b64url(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

    header = b64url(json.dumps({"alg": "none", "typ": "JWT"}).encode())
    payload = b64url(
        json.dumps(
            {"sub": user_id, "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp())}
        ).encode()
    )
    forged_token = f"{header}.{payload}."

    response = await async_client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {forged_token}"}
    )
    assert response.status_code == 401
