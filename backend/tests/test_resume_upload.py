"""Tests for POST /api/resume/upload."""
import pytest

from tests.test_resume_parser import make_docx_bytes, make_pdf_bytes


@pytest.fixture
def user_payload():
    return {"name": "Resume Uploader", "email": "uploader@example.com", "password": "supersecret123"}


@pytest.fixture
async def auth_headers(async_client, user_payload):
    response = await async_client.post("/api/auth/register", json=user_payload)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_upload_requires_auth(async_client):
    files = {"file": ("resume.pdf", make_pdf_bytes(), "application/pdf")}
    response = await async_client.post("/api/resume/upload", files=files)
    assert response.status_code == 401


async def test_upload_pdf_extracts_text(async_client, auth_headers):
    files = {"file": ("resume.pdf", make_pdf_bytes("Jane Doe\nPython Developer"), "application/pdf")}
    response = await async_client.post("/api/resume/upload", files=files, headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["file_type"] == "pdf"
    assert "Jane Doe" in body["extracted_text"]
    assert body["character_count"] > 0
    assert body["word_count"] > 0


async def test_upload_docx_extracts_text(async_client, auth_headers):
    files = {
        "file": (
            "resume.docx",
            make_docx_bytes(["Jane Doe", "Python Developer"]),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    }
    response = await async_client.post("/api/resume/upload", files=files, headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["file_type"] == "docx"
    assert "Jane Doe" in body["extracted_text"]


async def test_upload_rejects_unsupported_file_type(async_client, auth_headers):
    files = {"file": ("resume.txt", b"Jane Doe", "text/plain")}
    response = await async_client.post("/api/resume/upload", files=files, headers=auth_headers)

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


async def test_upload_rejects_empty_file(async_client, auth_headers):
    files = {"file": ("resume.pdf", b"", "application/pdf")}
    response = await async_client.post("/api/resume/upload", files=files, headers=auth_headers)

    assert response.status_code == 400
    assert "empty" in response.json()["detail"]


async def test_upload_rejects_malformed_pdf(async_client, auth_headers):
    files = {"file": ("resume.pdf", b"not a real pdf file", "application/pdf")}
    response = await async_client.post("/api/resume/upload", files=files, headers=auth_headers)

    assert response.status_code == 400
    assert "Couldn't read this PDF" in response.json()["detail"]
