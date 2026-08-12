"""Tests for the deterministic resume-vs-job-description matching engine."""
from app.services.jd_analyzer import analyze_job_description
from app.services.job_matcher import match_resume_to_job, score_experience_relevance, score_project_relevance
from app.services.resume_structurer import structure_resume

JOB_DESCRIPTION = """\
Backend Engineer

REQUIREMENTS
Strong experience with Python, FastAPI, and PostgreSQL.
Docker experience required.

PREFERRED SKILLS
AWS and Redis experience is a plus.

RESPONSIBILITIES
Build and maintain backend services.
"""

STRONG_MATCH_RESUME = """\
Jane Doe
jane@example.com

SKILLS
Python, FastAPI, PostgreSQL, Docker, AWS, Redis, Git

EXPERIENCE
Backend Engineer, Acme Corp
Built REST APIs with Python and FastAPI, deployed via Docker on AWS.

PROJECTS
Order Service - Built with FastAPI, PostgreSQL, and Redis caching.
"""

WEAK_MATCH_RESUME = """\
John Smith
john@example.com

SKILLS
HTML, CSS

EXPERIENCE
Marketing Assistant, Some Company
Wrote blog posts and managed social media accounts.
"""


def parsed_resume(text: str) -> dict:
    return structure_resume(text)


def parsed_job(text: str = JOB_DESCRIPTION) -> dict:
    return analyze_job_description(text)


def test_match_identifies_matching_and_missing_skills():
    result = match_resume_to_job(STRONG_MATCH_RESUME, parsed_resume(STRONG_MATCH_RESUME), parsed_job())
    assert "Python" in result["matching_skills"]
    assert "FastAPI" in result["matching_skills"]
    assert "Docker" in result["matching_skills"]
    assert result["missing_skills"] == []


def test_match_identifies_missing_skills_for_weak_resume():
    result = match_resume_to_job(WEAK_MATCH_RESUME, parsed_resume(WEAK_MATCH_RESUME), parsed_job())
    assert result["matching_skills"] == []
    assert "Python" in result["missing_skills"]
    assert "Docker" in result["missing_skills"]
    assert "AWS" in result["missing_skills"]


def test_match_matching_and_missing_skills_never_overlap():
    result = match_resume_to_job(STRONG_MATCH_RESUME, parsed_resume(STRONG_MATCH_RESUME), parsed_job())
    assert not set(result["matching_skills"]) & set(result["missing_skills"])


def test_match_keywords_reflect_technology_and_methodology_terms():
    result = match_resume_to_job(STRONG_MATCH_RESUME, parsed_resume(STRONG_MATCH_RESUME), parsed_job())
    assert "Python" in result["matching_keywords"]


def test_score_experience_relevance_rewards_demonstrated_skills():
    strong = score_experience_relevance(parsed_resume(STRONG_MATCH_RESUME), parsed_job())
    weak = score_experience_relevance(parsed_resume(WEAK_MATCH_RESUME), parsed_job())
    assert strong > weak


def test_score_project_relevance_rewards_demonstrated_skills():
    strong = score_project_relevance(parsed_resume(STRONG_MATCH_RESUME), parsed_job())
    weak = score_project_relevance(parsed_resume(WEAK_MATCH_RESUME), parsed_job())
    assert strong > weak


def test_overall_match_strong_resume_scores_higher_than_weak_resume():
    strong = match_resume_to_job(STRONG_MATCH_RESUME, parsed_resume(STRONG_MATCH_RESUME), parsed_job())
    weak = match_resume_to_job(WEAK_MATCH_RESUME, parsed_resume(WEAK_MATCH_RESUME), parsed_job())
    assert strong["overall_match"] > weak["overall_match"]
    assert strong["overall_match"] >= 70
    assert weak["overall_match"] <= 30


def test_overall_match_is_deterministic():
    first = match_resume_to_job(STRONG_MATCH_RESUME, parsed_resume(STRONG_MATCH_RESUME), parsed_job())
    second = match_resume_to_job(STRONG_MATCH_RESUME, parsed_resume(STRONG_MATCH_RESUME), parsed_job())
    assert first == second


def test_match_handles_job_description_with_no_detected_skills():
    # Should not divide by zero or crash — falls back to a neutral/full score.
    trivial_job = parsed_job("We are hiring for a role. Apply now.")
    result = match_resume_to_job(STRONG_MATCH_RESUME, parsed_resume(STRONG_MATCH_RESUME), trivial_job)
    assert result["missing_skills"] == []
    assert 0 <= result["overall_match"] <= 100


def test_explanation_mentions_missing_required_skills():
    result = match_resume_to_job(WEAK_MATCH_RESUME, parsed_resume(WEAK_MATCH_RESUME), parsed_job())
    assert any("required skill" in line.lower() for line in result["explanation"])


def test_all_scores_within_bounds():
    result = match_resume_to_job(STRONG_MATCH_RESUME, parsed_resume(STRONG_MATCH_RESUME), parsed_job())
    for field in ["overall_match", "experience_relevance", "project_relevance"]:
        assert 0 <= result[field] <= 100
