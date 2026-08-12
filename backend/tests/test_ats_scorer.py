"""Tests for the deterministic ATS scoring engine."""
from app.services.ats_scorer import (
    score_experience,
    score_formatting,
    score_keywords,
    score_projects,
    score_resume,
    score_skills,
    score_structure,
)
from app.services.resume_structurer import structure_resume

STRONG_RESUME = """\
Jane Doe
jane.doe@example.com | +1 555-123-4567
linkedin.com/in/janedoe | github.com/janedoe

SUMMARY
Full stack developer with 3 years of experience building scalable web applications.

SKILLS
Python, JavaScript, TypeScript, React, Node.js, FastAPI, MongoDB, PostgreSQL, Docker, Git, AWS

EDUCATION
B.Tech in Computer Science, XYZ University, 2020-2024

EXPERIENCE
Software Engineer, Acme Corp, Jun 2023 - Present
Developed 12 REST APIs serving over 50,000 requests per day.
Reduced page load time by 40% through caching and query optimization.
Led a team of 3 engineers to migrate the monolith to microservices.

PROJECTS
Resume Analyzer - Built an AI-powered resume scoring platform using React and FastAPI.
Increased test coverage from 40% to 90% across the codebase.
Task Manager App - Architected a real-time task tracker with Node.js and MongoDB.

CERTIFICATIONS
AWS Certified Solutions Architect

ACHIEVEMENTS
Winner, National Coding Hackathon 2023, among 500+ participants.
"""

WEAK_RESUME = """\
John Smith

I was responsible for various tasks and worked on some projects. I am a hard worker
and team player who is detail oriented and highly motivated. I helped with things
and duties included general support.
"""


def parsed(text: str) -> dict:
    return structure_resume(text)


def test_score_keywords_rewards_action_verbs_and_penalizes_weak_phrases():
    strong_score = score_keywords(STRONG_RESUME, parsed(STRONG_RESUME))
    weak_score = score_keywords(WEAK_RESUME, parsed(WEAK_RESUME))
    assert strong_score > weak_score


def test_score_skills_rewards_breadth_and_depth():
    rich = score_skills({"programming": ["Python", "Go"], "frontend": ["React"], "backend": ["FastAPI"], "database": ["MongoDB"], "tools": ["Docker", "Git"]})
    sparse = score_skills({"programming": ["Python"]})
    empty = score_skills({})
    assert rich > sparse > empty
    assert empty == 0


def test_score_structure_rewards_complete_sections():
    complete = score_structure(parsed(STRONG_RESUME))
    incomplete = score_structure(parsed("Just a name\nno other sections here"))
    assert complete > incomplete
    assert complete == 100  # STRONG_RESUME has every checklist item


def test_score_structure_never_exceeds_100():
    assert score_structure(parsed(STRONG_RESUME)) <= 100


def test_score_experience_rewards_metrics_and_coverage():
    with_metrics = score_experience(parsed(STRONG_RESUME))
    no_experience = score_experience(parsed("No experience section at all."))
    assert with_metrics > no_experience
    assert no_experience == 0


def test_score_projects_rewards_metrics_and_coverage():
    with_projects = score_projects(parsed(STRONG_RESUME))
    no_projects = score_projects(parsed("No projects here."))
    assert with_projects > no_projects
    assert no_projects == 0


def test_score_formatting_penalizes_extremely_short_resume():
    short_score = score_formatting("Just a few words here.")
    reasonable_score = score_formatting(STRONG_RESUME * 3)  # pad to a reasonable length
    assert reasonable_score > short_score


def test_score_formatting_penalizes_one_giant_paragraph():
    wall_of_text = " ".join(["word"] * 400)  # 400 words, one line
    bulleted = "\n".join(["Line with a few words here"] * 60)  # similar length, many lines
    assert score_formatting(bulleted) > score_formatting(wall_of_text)


def test_score_resume_returns_all_fields_within_bounds():
    result = score_resume(STRONG_RESUME, parsed(STRONG_RESUME))
    expected_keys = {
        "overall_score", "keyword_score", "skills_score", "structure_score",
        "experience_score", "project_score", "formatting_score",
    }
    assert set(result.keys()) == expected_keys
    for value in result.values():
        assert 0 <= value <= 100
        assert isinstance(value, int)


def test_score_resume_strong_resume_scores_higher_than_weak_resume():
    strong = score_resume(STRONG_RESUME, parsed(STRONG_RESUME))
    weak = score_resume(WEAK_RESUME, parsed(WEAK_RESUME))
    assert strong["overall_score"] > weak["overall_score"]


def test_score_resume_overall_is_deterministic():
    # Same input must always produce the same output — no randomness, no AI call.
    first = score_resume(STRONG_RESUME, parsed(STRONG_RESUME))
    second = score_resume(STRONG_RESUME, parsed(STRONG_RESUME))
    assert first == second


def test_score_resume_empty_text_scores_at_or_near_zero():
    empty_parsed = structure_resume("a")  # minimal non-empty text
    result = score_resume("a", empty_parsed)
    assert result["overall_score"] < 20
