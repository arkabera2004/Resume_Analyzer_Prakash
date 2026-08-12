"""Tests for the rule-based resume structuring service."""
from app.services.resume_structurer import (
    extract_contact_info,
    extract_skills,
    split_into_sections,
    structure_resume,
)

SAMPLE_RESUME = """\
Jane Doe
jane.doe@example.com | +1 555-123-4567
linkedin.com/in/janedoe | github.com/janedoe

SUMMARY
Full stack developer with 3 years of experience building web applications.

SKILLS
Python, JavaScript, React, Node.js, MongoDB, Docker, Git

EDUCATION
B.Tech in Computer Science, XYZ University, 2020-2024

EXPERIENCE
Software Engineer Intern, Acme Corp, Jun 2023 - Aug 2023
Built REST APIs using FastAPI and MongoDB.

PROJECTS
Resume Analyzer - AI-powered resume scoring platform built with React and FastAPI.

CERTIFICATIONS
AWS Certified Cloud Practitioner

ACHIEVEMENTS
Winner, University Hackathon 2023
"""


def test_extract_contact_info_finds_email_phone_and_links():
    contact = extract_contact_info(SAMPLE_RESUME)
    assert contact["name"] == "Jane Doe"
    assert contact["email"] == "jane.doe@example.com"
    assert contact["phone"] is not None
    assert "linkedin.com/in/janedoe" in contact["linkedin"]
    assert "github.com/janedoe" in contact["github"]


def test_extract_contact_info_handles_missing_fields_gracefully():
    contact = extract_contact_info("Just some text with no contact details at all.")
    assert contact["email"] is None
    assert contact["phone"] is None
    assert contact["linkedin"] is None
    assert contact["github"] is None


def test_split_into_sections_groups_lines_under_headers():
    sections = split_into_sections(SAMPLE_RESUME)
    assert "education" in sections
    assert any("XYZ University" in line for line in sections["education"])
    assert "experience" in sections
    assert any("Acme Corp" in line for line in sections["experience"])
    assert "projects" in sections
    assert any("Resume Analyzer" in line for line in sections["projects"])
    assert "certifications" in sections
    assert any("AWS" in line for line in sections["certifications"])
    assert "achievements" in sections
    assert any("Hackathon" in line for line in sections["achievements"])


def test_extract_skills_categorizes_known_keywords():
    skills = extract_skills(SAMPLE_RESUME)
    assert "Python" in skills["programming"]
    assert "JavaScript" in skills["programming"]
    assert "React" in skills["frontend"]
    assert "Node.js" in skills["backend"]
    assert "MongoDB" in skills["database"]
    assert "Docker" in skills["tools"]
    assert "Git" in skills["tools"]


def test_extract_skills_does_not_false_positive_on_substrings():
    # "Go" must not match inside "Google" or "Django" etc.
    skills = extract_skills("I used Google Cloud and Django for this project.")
    assert "Go" not in skills.get("programming", [])
    assert "Django" in skills.get("backend", [])


def test_extract_skills_does_not_double_count_overlapping_keywords():
    # "Node" is a substring of "Node.js" — only the longer, more specific keyword
    # should be reported.
    skills = extract_skills("Backend built with Node.js and Express.js.")
    assert "Node.js" in skills["backend"]
    assert "Node" not in skills["backend"]


def test_structure_resume_returns_full_shape():
    result = structure_resume(SAMPLE_RESUME)
    assert result["contact"]["name"] == "Jane Doe"
    assert "Python" in result["skills"]["programming"]
    assert len(result["education"]) > 0
    assert len(result["experience"]) > 0
    assert len(result["projects"]) > 0
    assert len(result["certifications"]) > 0
    assert len(result["achievements"]) > 0
    assert result["summary"] and "Full stack developer" in result["summary"]


def test_structure_resume_never_fabricates_missing_sections():
    minimal = "John Smith\njohn@example.com"
    result = structure_resume(minimal)
    assert result["education"] == []
    assert result["experience"] == []
    assert result["projects"] == []
    assert result["certifications"] == []
    assert result["achievements"] == []
