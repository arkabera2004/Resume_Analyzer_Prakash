"""Tests for POST /api/match/analyze."""
import pytest

RESUME_TEXT = """\
Jane Doe
jane@example.com

SKILLS
Python, React, MongoDB
"""

JOB_DESCRIPTION = """\
Full Stack Engineer

REQUIREMENTS
Python and React experience required.
"""


@pytest.fixture
def user_payload():
    return {"name": "Match User", "email": "matchuser@example.com", "password": "supersecret123"}


@pytest.fixture
async def auth_headers(async_client, user_payload):
    response = await async_client.post("/api/auth/register", json=user_payload)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_match_analyze_requires_auth(async_client):
    response = await async_client.post(
        "/api/match/analyze",
        json={"resume_text": RESUME_TEXT, "job_description": JOB_DESCRIPTION},
    )
    assert response.status_code == 401


async def test_match_analyze_returns_full_report(async_client, auth_headers):
    response = await async_client.post(
        "/api/match/analyze",
        json={"resume_text": RESUME_TEXT, "job_description": JOB_DESCRIPTION},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()

    assert "Python" in body["matching_skills"]
    assert "React" in body["matching_skills"]
    assert 0 <= body["overall_match"] <= 100
    assert body["parsed_job"]["job_title"] == "Full Stack Engineer"
    assert body["parsed_resume"]["contact"]["email"] == "jane@example.com"
    assert len(body["explanation"]) > 0


async def test_match_analyze_rejects_empty_resume_text(async_client, auth_headers):
    response = await async_client.post(
        "/api/match/analyze",
        json={"resume_text": "  ", "job_description": JOB_DESCRIPTION},
        headers=auth_headers,
    )
    assert response.status_code == 400


async def test_match_analyze_rejects_empty_job_description(async_client, auth_headers):
    response = await async_client.post(
        "/api/match/analyze",
        json={"resume_text": RESUME_TEXT, "job_description": "  "},
        headers=auth_headers,
    )
    assert response.status_code == 400
