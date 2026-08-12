"""Tests for PDF report generation."""
from app.services.report_service import build_analysis_report

FULL_ANALYSIS_DOC = {
    "resume_name": "jane_doe_resume.pdf",
    "job_title": "Backend Engineer",
    "parsed_resume": {
        "contact": {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "+1 555-123-4567",
            "linkedin": "linkedin.com/in/janedoe",
            "github": "github.com/janedoe",
        },
    },
    "ats_score": 82,
    "keyword_score": 80,
    "skills_score": 90,
    "structure_score": 85,
    "experience_score": 75,
    "project_score": 88,
    "formatting_score": 70,
    "match_score": 65,
    "matching_skills": ["Python", "React"],
    "missing_skills": ["Docker"],
    "matching_keywords": ["REST API"],
    "missing_keywords": ["CI/CD"],
    "strengths": ["Strong technical foundation"],
    "weaknesses": ["Limited leadership experience"],
    "priority_improvements": ["Add measurable results"],
}

MINIMAL_ANALYSIS_DOC = {
    "resume_name": "minimal.pdf",
    "parsed_resume": {},
}


def test_build_analysis_report_returns_valid_pdf_bytes():
    pdf_bytes = build_analysis_report(FULL_ANALYSIS_DOC)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 500  # a real rendered document, not an empty shell


def test_build_analysis_report_handles_minimal_document_without_crashing():
    # No scores, no match, no contact info, no recommendations — must not KeyError.
    pdf_bytes = build_analysis_report(MINIMAL_ANALYSIS_DOC)
    assert pdf_bytes.startswith(b"%PDF-")


def test_build_analysis_report_is_larger_with_more_content():
    minimal = build_analysis_report(MINIMAL_ANALYSIS_DOC)
    full = build_analysis_report(FULL_ANALYSIS_DOC)
    assert len(full) > len(minimal)
