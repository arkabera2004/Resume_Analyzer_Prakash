"""Tests for register/login/me/logout against a real MongoDB instance."""
import pytest


@pytest.fixture
def user_payload():
    return {"name": "Jane Doe", "email": "jane@example.com", "password": "supersecret123"}


async def test_register_creates_user_and_returns_token(async_client, user_payload):
    response = await async_client.post("/api/auth/register", json=user_payload)

    assert response.status_code == 201
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["email"] == user_payload["email"]
    assert body["user"]["name"] == user_payload["name"]
    assert "password" not in body["user"]
    assert "password_hash" not in body["user"]


async def test_register_duplicate_email_returns_409(async_client, user_payload):
    await async_client.post("/api/auth/register", json=user_payload)
    response = await async_client.post("/api/auth/register", json=user_payload)

    assert response.status_code == 409


async def test_register_rejects_short_password(async_client, user_payload):
    user_payload["password"] = "short"
    response = await async_client.post("/api/auth/register", json=user_payload)

    assert response.status_code == 422


async def test_login_with_correct_credentials_returns_token(async_client, user_payload):
    await async_client.post("/api/auth/register", json=user_payload)

    response = await async_client.post(
        "/api/auth/login",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )

    assert response.status_code == 200
    assert response.json()["access_token"]


async def test_login_with_wrong_password_returns_401(async_client, user_payload):
    await async_client.post("/api/auth/register", json=user_payload)

    response = await async_client.post(
        "/api/auth/login",
        json={"email": user_payload["email"], "password": "wrongpassword"},
    )

    assert response.status_code == 401


async def test_login_with_unknown_email_returns_401(async_client):
    response = await async_client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "whatever123"},
    )

    assert response.status_code == 401


async def test_me_without_token_returns_401(async_client):
    response = await async_client.get("/api/auth/me")
    assert response.status_code == 401


async def test_me_with_valid_token_returns_user(async_client, user_payload):
    register_response = await async_client.post("/api/auth/register", json=user_payload)
    token = register_response.json()["access_token"]

    response = await async_client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["email"] == user_payload["email"]


async def test_me_with_invalid_token_returns_401(async_client):
    response = await async_client.get(
        "/api/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401


async def test_logout_requires_auth(async_client, user_payload):
    register_response = await async_client.post("/api/auth/register", json=user_payload)
    token = register_response.json()["access_token"]

    authed = await async_client.post(
        "/api/auth/logout", headers={"Authorization": f"Bearer {token}"}
    )
    unauthed = await async_client.post("/api/auth/logout")

    assert authed.status_code == 200
    assert unauthed.status_code == 401
