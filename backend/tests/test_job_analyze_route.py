"""Tests for POST /api/job/analyze."""
import pytest

SAMPLE_JD = """\
Frontend Engineer

REQUIREMENTS
2+ years of experience with React and TypeScript.
"""


@pytest.fixture
def user_payload():
    return {"name": "JD Analyzer User", "email": "jdanalyzer@example.com", "password": "supersecret123"}


@pytest.fixture
async def auth_headers(async_client, user_payload):
    response = await async_client.post("/api/auth/register", json=user_payload)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_job_analyze_requires_auth(async_client):
    response = await async_client.post("/api/job/analyze", json={"job_description": SAMPLE_JD})
    assert response.status_code == 401


async def test_job_analyze_returns_structured_data(async_client, auth_headers):
    response = await async_client.post(
        "/api/job/analyze", json={"job_description": SAMPLE_JD}, headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["job_title"] == "Frontend Engineer"
    assert "React" in body["required_skills"]
    assert "TypeScript" in body["required_skills"]
    assert len(body["experience_requirements"]) >= 1


async def test_job_analyze_rejects_empty_description(async_client, auth_headers):
    response = await async_client.post(
        "/api/job/analyze", json={"job_description": "   "}, headers=auth_headers
    )
    assert response.status_code == 400
