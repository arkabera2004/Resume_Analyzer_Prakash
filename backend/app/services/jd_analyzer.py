"""Extracts structured information from a pasted job description.

Same philosophy as resume_structurer.py: rule-based (regex + keyword matching +
section-header splitting), not AI-generated, so it can't invent requirements that
aren't actually in the posting.
"""
import re

from app.services.jd_keywords import DEGREE_PHRASES, EXPERIENCE_PATTERNS, GENERAL_KEYWORDS
from app.services.keyword_matching import match_keywords
from app.services.skill_taxonomy import SKILL_CATEGORIES

# Section headers recognized when splitting a JD into blocks, mirroring
# resume_structurer's approach.
SECTION_ALIASES: dict[str, list[str]] = {
    "required": [
        "requirements", "required skills", "required qualifications",
        "minimum qualifications", "basic qualifications", "must have", "must-haves",
    ],
    "preferred": [
        "preferred skills", "preferred qualifications", "nice to have",
        "nice-to-haves", "bonus points", "good to have", "pluses",
    ],
    "responsibilities": [
        "responsibilities", "key responsibilities", "what you'll do",
        "what you will do", "role", "duties", "job description", "the role",
    ],
}
_ALIAS_TO_SECTION = {alias: section for section, aliases in SECTION_ALIASES.items() for alias in aliases}

_ALL_SKILL_KEYWORDS = [keyword for keywords in SKILL_CATEGORIES.values() for keyword in keywords]


def _is_section_header(line: str) -> str | None:
    cleaned = line.strip().strip(":").strip().lower()
    if not cleaned or len(cleaned) > 50:
        return None
    return _ALIAS_TO_SECTION.get(cleaned)


def split_into_sections(text: str) -> dict[str, list[str]]:
    """Split JD text into named sections based on recognized headers.

    Unlike resume section splitting, lines before the first header are kept under a
    "preamble" bucket — JDs often open straight into an intro/role summary with no
    header at all, and that's still useful text for keyword/skill detection.
    """
    sections: dict[str, list[str]] = {"preamble": []}
    current = "preamble"

    for raw_line in text.splitlines():
        line = raw_line.strip()
        header = _is_section_header(line)
        if header:
            current = header
            sections.setdefault(current, [])
            continue
        if line:
            sections[current].append(line)

    return sections


def extract_job_title(text: str) -> str | None:
    """Heuristic: the job title is usually the first short, non-header line."""
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if _is_section_header(line):
            return None
        if len(line) <= 80:
            return line
        return None
    return None


def extract_required_and_preferred_skills(
    text: str, sections: dict[str, list[str]]
) -> tuple[list[str], list[str]]:
    required_text = "\n".join(sections.get("required", []))
    preferred_text = "\n".join(sections.get("preferred", []))

    if not required_text and not preferred_text:
        # No distinct sections found — treat the whole JD as the requirements pool.
        required_skills = match_keywords(text, _ALL_SKILL_KEYWORDS)
        return required_skills, []

    required_skills = match_keywords(required_text or text, _ALL_SKILL_KEYWORDS)
    preferred_skills = match_keywords(preferred_text, _ALL_SKILL_KEYWORDS)
    # Don't list a skill as both required and preferred.
    preferred_skills = [skill for skill in preferred_skills if skill not in required_skills]

    return required_skills, preferred_skills


def extract_technologies(text: str) -> list[str]:
    """All technology/tool keywords mentioned anywhere in the JD."""
    return match_keywords(text, _ALL_SKILL_KEYWORDS)


def extract_keywords(text: str) -> list[str]:
    """Technologies plus methodology/process terms — the fuller set used for
    resume-vs-JD keyword matching in a later phase."""
    technologies = extract_technologies(text)
    general = match_keywords(text, GENERAL_KEYWORDS)
    # Preserve order, drop duplicates.
    seen = set()
    combined = []
    for keyword in technologies + general:
        if keyword not in seen:
            seen.add(keyword)
            combined.append(keyword)
    return combined


def extract_experience_requirements(text: str) -> list[str]:
    matches: list[str] = []
    seen_spans: list[tuple[int, int]] = []
    for pattern in EXPERIENCE_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            if any(start <= match.start() and match.end() <= end for start, end in seen_spans):
                continue
            matches.append(match.group(0).strip())
            seen_spans.append((match.start(), match.end()))
    return matches


def extract_education_requirements(text: str) -> list[str]:
    return match_keywords(text, DEGREE_PHRASES)


def analyze_job_description(text: str) -> dict:
    """Produce the full structured JSON for a job description's raw text."""
    sections = split_into_sections(text)
    required_skills, preferred_skills = extract_required_and_preferred_skills(text, sections)

    return {
        "job_title": extract_job_title(text),
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "technologies": extract_technologies(text),
        "keywords": extract_keywords(text),
        "experience_requirements": extract_experience_requirements(text),
        "education_requirements": extract_education_requirements(text),
        "responsibilities": sections.get("responsibilities", []),
    }
