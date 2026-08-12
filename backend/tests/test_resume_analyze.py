"""Tests for POST /api/resume/analyze."""
import pytest

SAMPLE_TEXT = """\
Jane Doe
jane.doe@example.com | +1 555-123-4567
linkedin.com/in/janedoe

SKILLS
Python, React, MongoDB

EXPERIENCE
Developed 5 internal tools used by the engineering team.
"""


@pytest.fixture
def user_payload():
    return {"name": "Analyzer User", "email": "analyzer@example.com", "password": "supersecret123"}


@pytest.fixture
async def auth_headers(async_client, user_payload):
    response = await async_client.post("/api/auth/register", json=user_payload)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_analyze_requires_auth(async_client):
    response = await async_client.post("/api/resume/analyze", json={"extracted_text": SAMPLE_TEXT})
    assert response.status_code == 401


async def test_analyze_returns_score_breakdown(async_client, auth_headers):
    response = await async_client.post(
        "/api/resume/analyze", json={"extracted_text": SAMPLE_TEXT}, headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()

    for field in [
        "overall_score", "keyword_score", "skills_score", "structure_score",
        "experience_score", "project_score", "formatting_score",
    ]:
        assert field in body
        assert 0 <= body[field] <= 100

    assert body["parsed"]["contact"]["email"] == "jane.doe@example.com"


async def test_analyze_rejects_empty_text(async_client, auth_headers):
    response = await async_client.post(
        "/api/resume/analyze", json={"extracted_text": "   "}, headers=auth_headers
    )
    assert response.status_code == 400
