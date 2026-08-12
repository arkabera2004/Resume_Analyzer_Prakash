"""Tests for POST /api/ai/improve-bullet, with the actual LLM call mocked out."""
from unittest.mock import patch

import pytest

from app.services.ai_service import AIServiceError

MOCK_RESULT = {
    "original": "Created an e-commerce website using React.",
    "improved": "Developed a responsive e-commerce platform using React with reusable components.",
    "why_better": ["Stronger action verb", "More technical detail"],
}


@pytest.fixture
def user_payload():
    return {"name": "Bullet User", "email": "bulletuser@example.com", "password": "supersecret123"}


@pytest.fixture
async def auth_headers(async_client, user_payload):
    response = await async_client.post("/api/auth/register", json=user_payload)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_improve_bullet_requires_auth(async_client):
    response = await async_client.post(
        "/api/ai/improve-bullet", json={"bullet_text": "Created a website."}
    )
    assert response.status_code == 401


async def test_improve_bullet_rejects_empty_text(async_client, auth_headers):
    response = await async_client.post(
        "/api/ai/improve-bullet", json={"bullet_text": "   "}, headers=auth_headers
    )
    assert response.status_code == 400


async def test_improve_bullet_rejects_oversized_text(async_client, auth_headers):
    response = await async_client.post(
        "/api/ai/improve-bullet", json={"bullet_text": "x" * 501}, headers=auth_headers
    )
    assert response.status_code == 422  # pydantic max_length validation


async def test_improve_bullet_returns_validated_ai_output(async_client, auth_headers):
    with patch("app.routes.ai.improve_bullet", return_value=MOCK_RESULT) as mock_improve:
        response = await async_client.post(
            "/api/ai/improve-bullet",
            json={"bullet_text": "Created an e-commerce website using React."},
            headers=auth_headers,
        )

    assert response.status_code == 200
    body = response.json()
    assert body["improved"] == MOCK_RESULT["improved"]
    assert body["why_better"] == MOCK_RESULT["why_better"]
    mock_improve.assert_called_once()


async def test_improve_bullet_passes_optional_context(async_client, auth_headers):
    with patch("app.routes.ai.improve_bullet", return_value=MOCK_RESULT) as mock_improve:
        await async_client.post(
            "/api/ai/improve-bullet",
            json={"bullet_text": "Built the backend.", "context": "Skills: Python, FastAPI"},
            headers=auth_headers,
        )
    mock_improve.assert_called_once_with("Built the backend.", "Skills: Python, FastAPI")


async def test_improve_bullet_returns_502_when_ai_service_fails(async_client, auth_headers):
    with patch(
        "app.routes.ai.improve_bullet",
        side_effect=AIServiceError("The AI service is temporarily unavailable. Please try again."),
    ):
        response = await async_client.post(
            "/api/ai/improve-bullet",
            json={"bullet_text": "Created a website."},
            headers=auth_headers,
        )

    assert response.status_code == 502
