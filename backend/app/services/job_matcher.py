"""Compares a parsed resume against a parsed job description.

Deterministic (set comparisons + weighted overlap scoring), not AI — same
philosophy as ats_scorer.py. AI is reserved for turning these facts into prose
recommendations in a later phase; the numbers and the "why" bullet points below are
always computed the same way for the same input.
"""
from app.services.jd_keywords import GENERAL_KEYWORDS
from app.services.keyword_matching import match_keywords
from app.services.skill_taxonomy import SKILL_CATEGORIES

_ALL_SKILL_KEYWORDS = [keyword for keywords in SKILL_CATEGORIES.values() for keyword in keywords]

WEIGHTS = {
    "skills": 0.50,
    "keywords": 0.20,
    "experience": 0.15,
    "projects": 0.15,
}


def _clamp(value: float, low: float = 0, high: float = 100) -> int:
    return int(round(max(low, min(high, value))))


def _flatten_resume_skills(parsed_resume: dict) -> set[str]:
    return {skill for skills in parsed_resume["skills"].values() for skill in skills}


def _extract_resume_keywords(resume_text: str) -> set[str]:
    """Resume-side equivalent of jd_analyzer.extract_keywords: technologies plus
    methodology/process terms, so the same "keywords" concept applies to both
    documents being compared."""
    technologies = match_keywords(resume_text, _ALL_SKILL_KEYWORDS)
    general = match_keywords(resume_text, GENERAL_KEYWORDS)
    return set(technologies) | set(general)


def _weighted_skill_overlap(
    required: list[str], preferred: list[str], haystack_text: str
) -> int:
    """What fraction of the JD's required/preferred skills show up in a given block
    of resume text — required skills count double, since missing a "must have" is
    worse than missing a "nice to have"."""
    if not required and not preferred:
        return 0

    weighted_total = len(required) * 2 + len(preferred)
    hits = sum(2 for skill in required if skill in haystack_text)
    hits += sum(1 for skill in preferred if skill in haystack_text)

    return _clamp((hits / weighted_total) * 100) if weighted_total else 0


def score_experience_relevance(parsed_resume: dict, parsed_job: dict) -> int:
    """How much of the JD's required/preferred skill set is actually demonstrated in
    the resume's experience/internship bullets (not just listed in a skills section),
    plus a small baseline for having substantive experience content at all."""
    experience_lines = parsed_resume["experience"] + parsed_resume["internships"]
    experience_text = "\n".join(experience_lines)

    skill_overlap = _weighted_skill_overlap(
        parsed_job["required_skills"], parsed_job["preferred_skills"], experience_text
    )
    coverage_bonus = min(20, len(experience_lines) * 4)

    # skill_overlap is 0-100; blend it down to 80% weight, leaving room for the bonus.
    return _clamp(skill_overlap * 0.8 + coverage_bonus)


def score_project_relevance(parsed_resume: dict, parsed_job: dict) -> int:
    """Same idea as experience relevance, applied to the projects section — often
    where a resume's most JD-relevant, hands-on technical evidence actually lives."""
    project_lines = parsed_resume["projects"]
    project_text = "\n".join(project_lines)

    skill_overlap = _weighted_skill_overlap(
        parsed_job["required_skills"], parsed_job["preferred_skills"], project_text
    )
    coverage_bonus = min(20, len(project_lines) * 5)

    return _clamp(skill_overlap * 0.8 + coverage_bonus)


def _build_explanation(
    matching_skills: list[str],
    missing_required_skills: list[str],
    missing_preferred_skills: list[str],
    experience_relevance: int,
    project_relevance: int,
    overall_match: int,
) -> list[str]:
    """Plain, templated statements of fact — not AI-generated prose — so the "why"
    behind the score is exactly as auditable as the score itself."""
    lines = []

    if matching_skills:
        lines.append(
            f"Resume matches {len(matching_skills)} skill(s) the job mentions: "
            + ", ".join(matching_skills[:8])
            + ("…" if len(matching_skills) > 8 else "")
        )
    else:
        lines.append("Resume doesn't currently mention any skills the job description asks for.")

    if missing_required_skills:
        lines.append(
            f"Missing {len(missing_required_skills)} required skill(s): "
            + ", ".join(missing_required_skills)
        )
    if missing_preferred_skills:
        lines.append(
            f"Missing {len(missing_preferred_skills)} preferred skill(s): "
            + ", ".join(missing_preferred_skills)
        )

    if experience_relevance >= 60:
        lines.append("Experience section demonstrates several of the job's required skills.")
    elif experience_relevance > 0:
        lines.append("Experience section only partially reflects the job's required skills.")
    else:
        lines.append("Experience section doesn't show the job's required skills in use.")

    if project_relevance >= 60:
        lines.append("Projects section is strongly aligned with this job's tech stack.")
    elif project_relevance > 0:
        lines.append("Projects section only partially overlaps with this job's tech stack.")
    else:
        lines.append("Projects section doesn't overlap with this job's tech stack.")

    if overall_match >= 75:
        lines.append("Overall, this resume is a strong match for this role.")
    elif overall_match >= 50:
        lines.append("Overall, this resume is a moderate match — some gaps to address.")
    else:
        lines.append("Overall, this resume is a weak match for this role as written.")

    return lines


def match_resume_to_job(resume_text: str, parsed_resume: dict, parsed_job: dict) -> dict:
    """Produce the full match report comparing a parsed resume to a parsed JD."""
    resume_skills = _flatten_resume_skills(parsed_resume)
    required_skills = set(parsed_job["required_skills"])
    preferred_skills = set(parsed_job["preferred_skills"])
    jd_skills = required_skills | preferred_skills

    matching_skills = sorted(resume_skills & jd_skills)
    missing_required_skills = sorted(required_skills - resume_skills)
    missing_preferred_skills = sorted(preferred_skills - resume_skills)
    missing_skills = sorted(set(missing_required_skills) | set(missing_preferred_skills))

    resume_keywords = _extract_resume_keywords(resume_text)
    jd_keywords = set(parsed_job["keywords"])
    matching_keywords = sorted(resume_keywords & jd_keywords)
    missing_keywords = sorted(jd_keywords - resume_keywords)

    skill_match_pct = (
        _clamp((len(matching_skills) / len(jd_skills)) * 100) if jd_skills else 100
    )
    keyword_match_pct = (
        _clamp((len(matching_keywords) / len(jd_keywords)) * 100) if jd_keywords else 100
    )
    experience_relevance = score_experience_relevance(parsed_resume, parsed_job)
    project_relevance = score_project_relevance(parsed_resume, parsed_job)

    overall_match = _clamp(
        skill_match_pct * WEIGHTS["skills"]
        + keyword_match_pct * WEIGHTS["keywords"]
        + experience_relevance * WEIGHTS["experience"]
        + project_relevance * WEIGHTS["projects"]
    )

    explanation = _build_explanation(
        matching_skills,
        missing_required_skills,
        missing_preferred_skills,
        experience_relevance,
        project_relevance,
        overall_match,
    )

    return {
        "overall_match": overall_match,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "matching_keywords": matching_keywords,
        "missing_keywords": missing_keywords,
        "experience_relevance": experience_relevance,
        "project_relevance": project_relevance,
        "explanation": explanation,
    }
