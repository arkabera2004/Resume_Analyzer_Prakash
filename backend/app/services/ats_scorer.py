"""Deterministic ATS scoring engine.

This is the ONLY source of the numeric ATS score in the app. Every sub-score is a
plain, auditable calculation over the resume's raw text and its parsed structure
(from resume_structurer.py) — no LLM is involved in producing these numbers, per the
project's explicit requirement that scores be transparent and reproducible. An AI
service may later *explain* the score in prose, but never invent it.

Weights (sum to 100%), matching the project spec:
    Keyword Match        30%
    Skills Match         25%
    Resume Structure     15%
    Experience Relevance 15%
    Project Relevance    10%
    Formatting            5%
"""
import re

from app.services.ats_keywords import STRONG_ACTION_VERBS, WEAK_PHRASES

WEIGHTS = {
    "keyword": 0.30,
    "skills": 0.25,
    "structure": 0.15,
    "experience": 0.15,
    "project": 0.10,
    "formatting": 0.05,
}

_HAS_DIGIT_OR_METRIC = re.compile(r"\d")
_FIRST_WORD = re.compile(r"^[\W_]*([A-Za-z]+)")


def _clamp(value: float, low: float = 0, high: float = 100) -> int:
    return int(round(max(low, min(high, value))))


def _first_word(line: str) -> str:
    match = _FIRST_WORD.match(line)
    return match.group(1).lower() if match else ""


def score_keywords(text: str, parsed: dict) -> int:
    """Rewards strong action verbs and technical keyword density; penalizes
    well-known weak/passive phrases. This substitutes for job-description keyword
    matching, which isn't available here — see job_matcher.py (Phase 9) for the
    JD-aware version of keyword scoring."""
    bullet_lines = parsed["experience"] + parsed["internships"] + parsed["projects"]

    if bullet_lines:
        strong_verb_hits = sum(1 for line in bullet_lines if _first_word(line) in STRONG_ACTION_VERBS)
        action_verb_score = min(50, round((strong_verb_hits / len(bullet_lines)) * 50))
    else:
        action_verb_score = 0

    word_count = max(1, len(text.split()))
    skill_count = sum(len(v) for v in parsed["skills"].values())
    # ~1 technical keyword per 25 words is a reasonable, keyword-rich resume; scale
    # linearly up to that density for the full 30 points.
    density_score = min(30, round((skill_count / max(1, word_count / 25)) * 30))

    lowered = text.lower()
    weak_phrase_hits = sum(1 for phrase in WEAK_PHRASES if phrase in lowered)
    weak_phrase_penalty = min(20, weak_phrase_hits * 5)

    return _clamp(action_verb_score + density_score + 20 - weak_phrase_penalty)


def score_skills(skills: dict[str, list[str]]) -> int:
    """Rewards both breadth (skill categories covered) and depth (total skills)."""
    unique_count = sum(len(v) for v in skills.values())
    categories_covered = len(skills)

    depth_score = min(70, unique_count * 5)  # 14+ skills maxes this out
    breadth_score = min(30, categories_covered * 6)  # all 5 categories maxes this out

    return _clamp(depth_score + breadth_score)


def score_structure(parsed: dict) -> int:
    """Checks for the presence of the sections/fields a resume is expected to have."""
    contact = parsed["contact"]
    checklist = [
        bool(contact.get("name")),
        bool(contact.get("email")),
        bool(contact.get("phone")),
        bool(contact.get("linkedin") or contact.get("github")),
        bool(parsed.get("summary")),
        bool(parsed["education"]),
        bool(parsed["experience"] or parsed["internships"]),
        bool(parsed["skills"]),
        bool(parsed["projects"]),
    ]
    return _clamp((sum(checklist) / len(checklist)) * 100)


def _score_bullet_section(lines: list[str], max_lines_for_full_score: int) -> int:
    """Shared logic for experience/project scoring: rewards having enough bullet
    lines and rewards those lines containing quantifiable metrics (numbers/%/$),
    another well-established ATS/recruiter heuristic ("increased X by 30%" beats
    "worked on X")."""
    if not lines:
        return 0

    coverage_score = min(60, round((len(lines) / max_lines_for_full_score) * 60))
    metric_hits = sum(1 for line in lines if _HAS_DIGIT_OR_METRIC.search(line))
    metric_score = min(40, round((metric_hits / len(lines)) * 40))

    return _clamp(coverage_score + metric_score)


def score_experience(parsed: dict) -> int:
    lines = parsed["experience"] + parsed["internships"]
    return _score_bullet_section(lines, max_lines_for_full_score=6)


def score_projects(parsed: dict) -> int:
    return _score_bullet_section(parsed["projects"], max_lines_for_full_score=4)


def score_formatting(text: str) -> int:
    """Checks resume length is in a reasonable range and that it reads as
    bullet/line-structured rather than one dense wall of text — both standard
    ATS-parseability concerns."""
    word_count = len(text.split())
    line_count = len([line for line in text.splitlines() if line.strip()])

    # 250-900 words is a reasonable 1-2 page resume; scaled penalty outside that.
    if 250 <= word_count <= 900:
        length_score = 70
    elif word_count < 250:
        length_score = max(0, round(70 * (word_count / 250)))
    else:
        overflow = word_count - 900
        length_score = max(0, 70 - round(overflow / 20))

    words_per_line = word_count / max(1, line_count)
    # A resume that's mostly short lines (bullets/headers) parses far better than
    # a few giant paragraphs. ~12 words/line or fewer scores full marks.
    if words_per_line <= 12:
        structure_score = 30
    else:
        structure_score = max(0, 30 - round((words_per_line - 12) * 2))

    return _clamp(length_score + structure_score)


def score_resume(text: str, parsed: dict) -> dict[str, int]:
    """Compute every sub-score and the weighted overall ATS score."""
    keyword_score = score_keywords(text, parsed)
    skills_score = score_skills(parsed["skills"])
    structure_score = score_structure(parsed)
    experience_score = score_experience(parsed)
    project_score = score_projects(parsed)
    formatting_score = score_formatting(text)

    overall = (
        keyword_score * WEIGHTS["keyword"]
        + skills_score * WEIGHTS["skills"]
        + structure_score * WEIGHTS["structure"]
        + experience_score * WEIGHTS["experience"]
        + project_score * WEIGHTS["project"]
        + formatting_score * WEIGHTS["formatting"]
    )

    return {
        "overall_score": _clamp(overall),
        "keyword_score": keyword_score,
        "skills_score": skills_score,
        "structure_score": structure_score,
        "experience_score": experience_score,
        "project_score": project_score,
        "formatting_score": formatting_score,
    }
