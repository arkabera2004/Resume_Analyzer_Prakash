"""Tests for GET /api/analysis/{id}/report."""
import pytest

SAVE_PAYLOAD = {
    "resume_name": "jane_doe_resume.pdf",
    "job_title": "Backend Engineer",
    "parsed_resume": {"contact": {"name": "Jane Doe", "email": "jane@example.com"}},
    "ats_score": 82,
    "match_score": 65,
    "matching_skills": ["Python"],
    "missing_skills": ["Docker"],
}


@pytest.fixture
def user_payload():
    return {"name": "Report User", "email": "reportuser@example.com", "password": "supersecret123"}


@pytest.fixture
async def auth_headers(async_client, user_payload):
    response = await async_client.post("/api/auth/register", json=user_payload)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def other_user_headers(async_client):
    response = await async_client.post(
        "/api/auth/register",
        json={"name": "Other", "email": "reportother@example.com", "password": "supersecret123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_download_report_requires_auth(async_client):
    response = await async_client.get("/api/analysis/000000000000000000000000/report")
    assert response.status_code == 401


async def test_download_report_returns_pdf(async_client, auth_headers):
    save_response = await async_client.post(
        "/api/analysis/save", json=SAVE_PAYLOAD, headers=auth_headers
    )
    analysis_id = save_response.json()["id"]

    response = await async_client.get(f"/api/analysis/{analysis_id}/report", headers=auth_headers)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers["content-disposition"]
    assert "jane_doe_resume" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF-")


async def test_download_report_returns_404_for_unowned_analysis(
    async_client, auth_headers, other_user_headers
):
    save_response = await async_client.post(
        "/api/analysis/save", json=SAVE_PAYLOAD, headers=auth_headers
    )
    analysis_id = save_response.json()["id"]

    response = await async_client.get(
        f"/api/analysis/{analysis_id}/report", headers=other_user_headers
    )
    assert response.status_code == 404


async def test_download_report_returns_404_for_missing_analysis(async_client, auth_headers):
    response = await async_client.get(
        "/api/analysis/000000000000000000000000/report", headers=auth_headers
    )
    assert response.status_code == 404
