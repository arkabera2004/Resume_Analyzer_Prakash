"""Tests for POST /api/analysis/compare."""
import asyncio

import pytest

OLDER_ANALYSIS = {
    "resume_name": "resume_v1.pdf",
    "parsed_resume": {"skills": {"programming": ["Python"], "backend": ["Flask"]}},
    "ats_score": 60,
    "match_score": 50,
    "matching_keywords": ["Python", "REST API"],
    "section_scores": {
        "skills": {"score": 5, "strengths": [], "problems": [], "recommendations": []},
        "summary": {"score": 3, "strengths": [], "problems": [], "recommendations": []},
    },
}

NEWER_ANALYSIS = {
    "resume_name": "resume_v2.pdf",
    "parsed_resume": {"skills": {"programming": ["Python", "TypeScript"], "backend": ["FastAPI"]}},
    "ats_score": 85,
    "match_score": 40,
    "matching_keywords": ["Python", "Docker"],
    "section_scores": {
        "skills": {"score": 9, "strengths": [], "problems": [], "recommendations": []},
        "summary": {"score": 1, "strengths": [], "problems": [], "recommendations": []},
    },
}


@pytest.fixture
def user_payload():
    return {"name": "Compare User", "email": "compareuser@example.com", "password": "supersecret123"}


@pytest.fixture
async def auth_headers(async_client, user_payload):
    response = await async_client.post("/api/auth/register", json=user_payload)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def other_user_headers(async_client):
    response = await async_client.post(
        "/api/auth/register",
        json={"name": "Other", "email": "compareother@example.com", "password": "supersecret123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def _save_two(async_client, auth_headers):
    older_response = await async_client.post(
        "/api/analysis/save", json=OLDER_ANALYSIS, headers=auth_headers
    )
    await asyncio.sleep(0.01)  # ensure distinct created_at ordering
    newer_response = await async_client.post(
        "/api/analysis/save", json=NEWER_ANALYSIS, headers=auth_headers
    )
    return older_response.json()["id"], newer_response.json()["id"]


async def test_compare_requires_auth(async_client):
    response = await async_client.post(
        "/api/analysis/compare",
        json={"analysis_id_a": "a" * 24, "analysis_id_b": "b" * 24},
    )
    assert response.status_code == 401


async def test_compare_rejects_identical_ids(async_client, auth_headers):
    older_id, _ = await _save_two(async_client, auth_headers)
    response = await async_client.post(
        "/api/analysis/compare",
        json={"analysis_id_a": older_id, "analysis_id_b": older_id},
        headers=auth_headers,
    )
    assert response.status_code == 400


async def test_compare_computes_score_changes(async_client, auth_headers):
    older_id, newer_id = await _save_two(async_client, auth_headers)

    response = await async_client.post(
        "/api/analysis/compare",
        json={"analysis_id_a": older_id, "analysis_id_b": newer_id},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()

    assert body["ats_score_change"] == 25  # 85 - 60
    assert body["match_score_change"] == -10  # 40 - 50
    assert "TypeScript" in body["new_skills"]
    assert "FastAPI" in body["new_skills"]
    assert "Flask" in body["removed_skills"]
    assert "Python" not in body["new_skills"]  # unchanged, shouldn't appear either way
    assert "Docker" in body["new_keywords"]
    assert "REST API" in body["removed_keywords"]
    assert "skills" in body["improved_sections"]
    assert "summary" in body["regressed_sections"]


async def test_compare_result_is_order_independent(async_client, auth_headers):
    older_id, newer_id = await _save_two(async_client, auth_headers)

    forward = await async_client.post(
        "/api/analysis/compare",
        json={"analysis_id_a": older_id, "analysis_id_b": newer_id},
        headers=auth_headers,
    )
    backward = await async_client.post(
        "/api/analysis/compare",
        json={"analysis_id_a": newer_id, "analysis_id_b": older_id},
        headers=auth_headers,
    )

    # Regardless of argument order, "a" in the response is always the older one.
    assert forward.json()["ats_score_change"] == backward.json()["ats_score_change"]
    assert forward.json()["analysis_a"]["resume_name"] == "resume_v1.pdf"
    assert backward.json()["analysis_a"]["resume_name"] == "resume_v1.pdf"


async def test_compare_returns_404_for_unowned_analysis(
    async_client, auth_headers, other_user_headers
):
    older_id, newer_id = await _save_two(async_client, auth_headers)

    response = await async_client.post(
        "/api/analysis/compare",
        json={"analysis_id_a": older_id, "analysis_id_b": newer_id},
        headers=other_user_headers,
    )
    assert response.status_code == 404
