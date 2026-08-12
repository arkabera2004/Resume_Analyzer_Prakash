"""Tests for /api/analysis/* (save, history, get, delete) and /api/dashboard/stats."""
import pytest

SAVE_PAYLOAD_A = {
    "resume_name": "resume_v1.pdf",
    "job_title": "Backend Engineer",
    "parsed_resume": {"skills": {"programming": ["Python"], "backend": ["FastAPI"]}},
    "ats_score": 72,
    "match_score": 60,
}

SAVE_PAYLOAD_B = {
    "resume_name": "resume_v2.pdf",
    "job_title": "Full Stack Engineer",
    "parsed_resume": {"skills": {"programming": ["Python", "JavaScript"], "frontend": ["React"]}},
    "ats_score": 88,
    "match_score": 80,
}


@pytest.fixture
def user_payload():
    return {"name": "Analysis User", "email": "analysisuser@example.com", "password": "supersecret123"}


@pytest.fixture
async def auth_headers(async_client, user_payload):
    response = await async_client.post("/api/auth/register", json=user_payload)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def other_user_headers(async_client):
    response = await async_client.post(
        "/api/auth/register",
        json={"name": "Other User", "email": "otheruser@example.com", "password": "supersecret123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_save_analysis_requires_auth(async_client):
    response = await async_client.post("/api/analysis/save", json=SAVE_PAYLOAD_A)
    assert response.status_code == 401


async def test_save_analysis_returns_full_detail(async_client, auth_headers):
    response = await async_client.post("/api/analysis/save", json=SAVE_PAYLOAD_A, headers=auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["resume_name"] == "resume_v1.pdf"
    assert body["ats_score"] == 72
    assert "id" in body
    assert "created_at" in body


async def test_history_returns_only_own_analyses_newest_first(async_client, auth_headers):
    await async_client.post("/api/analysis/save", json=SAVE_PAYLOAD_A, headers=auth_headers)
    await async_client.post("/api/analysis/save", json=SAVE_PAYLOAD_B, headers=auth_headers)

    response = await async_client.get("/api/analysis/history", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["resume_name"] == "resume_v2.pdf"  # newest first
    assert body[1]["resume_name"] == "resume_v1.pdf"


async def test_history_requires_auth(async_client):
    response = await async_client.get("/api/analysis/history")
    assert response.status_code == 401


async def test_get_analysis_by_id_returns_full_detail(async_client, auth_headers):
    save_response = await async_client.post(
        "/api/analysis/save", json=SAVE_PAYLOAD_A, headers=auth_headers
    )
    analysis_id = save_response.json()["id"]

    response = await async_client.get(f"/api/analysis/{analysis_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["resume_name"] == "resume_v1.pdf"


async def test_get_analysis_returns_404_for_unowned_analysis(
    async_client, auth_headers, other_user_headers
):
    save_response = await async_client.post(
        "/api/analysis/save", json=SAVE_PAYLOAD_A, headers=auth_headers
    )
    analysis_id = save_response.json()["id"]

    response = await async_client.get(f"/api/analysis/{analysis_id}", headers=other_user_headers)
    assert response.status_code == 404


async def test_get_analysis_returns_404_for_invalid_id(async_client, auth_headers):
    response = await async_client.get("/api/analysis/not-a-real-id", headers=auth_headers)
    assert response.status_code == 404


async def test_delete_analysis_removes_it(async_client, auth_headers):
    save_response = await async_client.post(
        "/api/analysis/save", json=SAVE_PAYLOAD_A, headers=auth_headers
    )
    analysis_id = save_response.json()["id"]

    delete_response = await async_client.delete(f"/api/analysis/{analysis_id}", headers=auth_headers)
    assert delete_response.status_code == 204

    get_response = await async_client.get(f"/api/analysis/{analysis_id}", headers=auth_headers)
    assert get_response.status_code == 404


async def test_delete_analysis_returns_404_for_unowned_analysis(
    async_client, auth_headers, other_user_headers
):
    save_response = await async_client.post(
        "/api/analysis/save", json=SAVE_PAYLOAD_A, headers=auth_headers
    )
    analysis_id = save_response.json()["id"]

    response = await async_client.delete(f"/api/analysis/{analysis_id}", headers=other_user_headers)
    assert response.status_code == 404

    # Confirm it wasn't actually deleted.
    still_there = await async_client.get(f"/api/analysis/{analysis_id}", headers=auth_headers)
    assert still_there.status_code == 200


async def test_dashboard_stats_with_no_analyses(async_client, auth_headers):
    response = await async_client.get("/api/dashboard/stats", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total_analyses"] == 0
    assert body["best_ats_score"] is None
    assert body["avg_match_score"] is None
    assert body["unique_skills_count"] == 0
    assert body["recent_analyses"] == []


async def test_dashboard_stats_aggregates_correctly(async_client, auth_headers):
    await async_client.post("/api/analysis/save", json=SAVE_PAYLOAD_A, headers=auth_headers)
    await async_client.post("/api/analysis/save", json=SAVE_PAYLOAD_B, headers=auth_headers)

    response = await async_client.get("/api/dashboard/stats", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()

    assert body["total_analyses"] == 2
    assert body["best_ats_score"] == 88  # max(72, 88)
    assert body["avg_match_score"] == 70  # avg(60, 80)
    # Unique skills across both: Python, FastAPI, JavaScript, React
    assert body["unique_skills_count"] == 4
    assert len(body["recent_analyses"]) == 2


async def test_dashboard_stats_only_counts_own_analyses(
    async_client, auth_headers, other_user_headers
):
    await async_client.post("/api/analysis/save", json=SAVE_PAYLOAD_A, headers=other_user_headers)

    response = await async_client.get("/api/dashboard/stats", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total_analyses"] == 0
