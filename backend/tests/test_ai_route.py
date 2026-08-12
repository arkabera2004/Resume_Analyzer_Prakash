"""Tests for POST /api/ai/recommendations, with the actual LLM call mocked out —
fast, free, and deterministic. See README for how to manually verify against the
real configured provider."""
from unittest.mock import patch

import pytest

from app.services.ai_service import AIServiceError

RESUME_TEXT = """\
Jane Doe
jane@example.com

SKILLS
Python, React
"""

MOCK_RECOMMENDATIONS = {
    "section_scores": {
        "summary": {"score": 5, "strengths": [], "problems": ["No summary present"], "recommendations": ["Add one"]},
    },
    "strengths": ["Solid technical foundation"],
    "weaknesses": ["No summary section"],
    "priority_improvements": ["Add a professional summary"],
    "recommended_roles": [{"role": "Frontend Developer", "match_percentage": 75, "reason": "React experience"}],
}


@pytest.fixture
def user_payload():
    return {"name": "AI User", "email": "aiuser@example.com", "password": "supersecret123"}


@pytest.fixture
async def auth_headers(async_client, user_payload):
    response = await async_client.post("/api/auth/register", json=user_payload)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_recommendations_requires_auth(async_client):
    response = await async_client.post("/api/ai/recommendations", json={"resume_text": RESUME_TEXT})
    assert response.status_code == 401


async def test_recommendations_rejects_empty_text(async_client, auth_headers):
    response = await async_client.post(
        "/api/ai/recommendations", json={"resume_text": "  "}, headers=auth_headers
    )
    assert response.status_code == 400


async def test_recommendations_returns_validated_ai_output(async_client, auth_headers):
    with patch(
        "app.routes.ai.get_ai_recommendations", return_value=MOCK_RECOMMENDATIONS
    ) as mock_recs:
        response = await async_client.post(
            "/api/ai/recommendations", json={"resume_text": RESUME_TEXT}, headers=auth_headers
        )

    assert response.status_code == 200
    body = response.json()
    assert body["strengths"] == ["Solid technical foundation"]
    assert body["recommended_roles"][0]["role"] == "Frontend Developer"
    mock_recs.assert_called_once()


async def test_recommendations_returns_502_when_ai_service_fails(async_client, auth_headers):
    with patch(
        "app.routes.ai.get_ai_recommendations",
        side_effect=AIServiceError("The AI service is temporarily unavailable. Please try again."),
    ):
        response = await async_client.post(
            "/api/ai/recommendations", json={"resume_text": RESUME_TEXT}, headers=auth_headers
        )

    assert response.status_code == 502
    assert "temporarily unavailable" in response.json()["detail"]
