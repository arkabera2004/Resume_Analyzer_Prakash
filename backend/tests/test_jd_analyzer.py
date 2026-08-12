"""Tests for the rule-based job-description analyzer."""
from app.services.jd_analyzer import (
    analyze_job_description,
    extract_education_requirements,
    extract_experience_requirements,
    extract_job_title,
    extract_keywords,
    extract_required_and_preferred_skills,
    extract_technologies,
    split_into_sections,
)

SAMPLE_JD = """\
Backend Software Engineer

We are looking for a Backend Software Engineer to join our growing team.

REQUIREMENTS
3+ years of experience in backend development.
Bachelor's degree in Computer Science or related field.
Strong experience with Python, FastAPI, and PostgreSQL.
Familiarity with Docker and CI/CD pipelines.

PREFERRED SKILLS
Experience with React and MongoDB is a plus.
Knowledge of Kubernetes and AWS.

RESPONSIBILITIES
Design and build REST APIs used by millions of users.
Collaborate with frontend engineers on API contracts.
Mentor junior engineers.
"""


def test_extract_job_title_returns_first_line():
    assert extract_job_title(SAMPLE_JD) == "Backend Software Engineer"


def test_split_into_sections_captures_preamble_and_headers():
    sections = split_into_sections(SAMPLE_JD)
    assert any("Backend Software Engineer" in line for line in sections["preamble"])
    assert "required" in sections
    assert "preferred" in sections
    assert "responsibilities" in sections
    assert any("REST APIs" in line for line in sections["responsibilities"])


def test_extract_required_and_preferred_skills_are_distinct():
    sections = split_into_sections(SAMPLE_JD)
    required, preferred = extract_required_and_preferred_skills(SAMPLE_JD, sections)
    assert "Python" in required
    assert "FastAPI" in required
    assert "PostgreSQL" in required
    assert "React" in preferred
    assert "MongoDB" in preferred
    # No overlap between the two buckets.
    assert not set(required) & set(preferred)


def test_extract_required_and_preferred_skills_falls_back_to_whole_text_pool():
    # No REQUIREMENTS/PREFERRED headers at all.
    text = "We need someone who knows Python and React."
    required, preferred = extract_required_and_preferred_skills(text, split_into_sections(text))
    assert "Python" in required
    assert "React" in required
    assert preferred == []


def test_extract_technologies_covers_whole_document():
    technologies = extract_technologies(SAMPLE_JD)
    assert "Python" in technologies
    assert "Docker" in technologies
    assert "Kubernetes" in technologies


def test_extract_keywords_includes_methodology_terms():
    keywords = extract_keywords(SAMPLE_JD)
    assert "CI/CD" in keywords
    assert "Python" in keywords  # technologies are included too


def test_extract_experience_requirements_finds_years():
    requirements = extract_experience_requirements(SAMPLE_JD)
    assert any("3" in req and "year" in req.lower() for req in requirements)


def test_extract_experience_requirements_returns_empty_when_absent():
    assert extract_experience_requirements("No years mentioned here.") == []


def test_extract_education_requirements_finds_degree_phrases():
    education = extract_education_requirements(SAMPLE_JD)
    assert "Bachelor's degree" in education
    # Should not also report the shorter "Bachelor" contained within it.
    assert "Bachelor" not in education


def test_extract_education_requirements_returns_empty_when_absent():
    assert extract_education_requirements("No degree mentioned here.") == []


def test_analyze_job_description_returns_full_shape():
    result = analyze_job_description(SAMPLE_JD)
    assert result["job_title"] == "Backend Software Engineer"
    assert "Python" in result["required_skills"]
    assert "React" in result["preferred_skills"]
    assert len(result["responsibilities"]) == 3
    assert len(result["experience_requirements"]) >= 1
    assert "Bachelor's degree" in result["education_requirements"]


def test_analyze_job_description_never_fabricates_missing_fields():
    minimal = "Software Engineer"
    result = analyze_job_description(minimal)
    assert result["required_skills"] == []
    assert result["preferred_skills"] == []
    assert result["experience_requirements"] == []
    assert result["education_requirements"] == []
    assert result["responsibilities"] == []
