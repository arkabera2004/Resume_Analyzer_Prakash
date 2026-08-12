"""Extracts structured information from raw resume text.

Deliberately rule-based (regex + keyword matching + section-header splitting), not
AI-generated — deterministic, explainable, and free of hallucination risk. AI is
reserved for the *recommendation* features (later phases), never for asserting facts
about what's in the resume.
"""
import re

from app.services.skill_taxonomy import SKILL_CATEGORIES

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(?:\+\d{1,3}[\s-]?)?(?:\(\d{2,4}\)[\s-]?)?\d{3,5}[\s-]?\d{3,4}[\s-]?\d{0,4}")
LINKEDIN_RE = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/[^\s,)]+", re.IGNORECASE)
GITHUB_RE = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[^\s,)]+", re.IGNORECASE)

# Section headers we recognize when splitting the resume into blocks. Matched against
# a whole line (case-insensitive) after stripping punctuation, so "EDUCATION",
# "Education:", and "Education " all match.
SECTION_ALIASES: dict[str, list[str]] = {
    "summary": ["summary", "objective", "profile", "about"],
    "education": ["education", "academic background", "academics"],
    "skills": ["skills", "technical skills", "core competencies"],
    "experience": ["experience", "work experience", "employment history", "professional experience"],
    "internships": ["internships", "internship experience"],
    "projects": ["projects", "personal projects", "academic projects"],
    "certifications": ["certifications", "certificates", "licenses"],
    "achievements": ["achievements", "awards", "honors", "accomplishments"],
}
_ALIAS_TO_SECTION = {alias: section for section, aliases in SECTION_ALIASES.items() for alias in aliases}

MIN_PHONE_DIGITS = 7


def _is_section_header(line: str) -> str | None:
    """Return the canonical section name if `line` looks like a section header."""
    cleaned = line.strip().strip(":").strip().lower()
    if not cleaned or len(cleaned) > 40:
        return None
    return _ALIAS_TO_SECTION.get(cleaned)


def split_into_sections(text: str) -> dict[str, list[str]]:
    """Split resume text into named sections based on recognized headers.

    Lines before the first recognized header are discarded (typically contact info,
    already handled separately). Returns {section_name: [non-empty lines]}.
    """
    sections: dict[str, list[str]] = {}
    current: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        header = _is_section_header(line)
        if header:
            current = header
            sections.setdefault(current, [])
            continue
        if current and line:
            sections[current].append(line)

    return sections


def extract_contact_info(text: str) -> dict[str, str | None]:
    email_match = EMAIL_RE.search(text)
    linkedin_match = LINKEDIN_RE.search(text)
    github_match = GITHUB_RE.search(text)

    phone = None
    for candidate in PHONE_RE.findall(text):
        digits = re.sub(r"\D", "", candidate)
        if len(digits) >= MIN_PHONE_DIGITS:
            phone = candidate.strip()
            break

    return {
        "name": _guess_name(text),
        "email": email_match.group(0) if email_match else None,
        "phone": phone,
        "linkedin": linkedin_match.group(0) if linkedin_match else None,
        "github": github_match.group(0) if github_match else None,
    }


def _guess_name(text: str) -> str | None:
    """Heuristic: the name is usually the first non-empty line, unless that line is
    actually contact info (email/phone/URL) or a recognized section header."""
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if EMAIL_RE.search(line) or LINKEDIN_RE.search(line) or GITHUB_RE.search(line):
            return None
        if _is_section_header(line):
            return None
        # A plausible name: short, mostly letters/spaces, no digits.
        if len(line) <= 60 and not any(char.isdigit() for char in line):
            return line
        return None
    return None


def extract_skills(text: str) -> dict[str, list[str]]:
    """Keyword-match the whole resume against the skill taxonomy, category by category.

    Keywords are checked longest-first so "Node.js" is matched (and kept) before the
    shorter "Node" is even tried against the same span — otherwise a resume that only
    says "Node.js" would confusingly report both "Node.js" and "Node" as separate hits.
    """
    found: dict[str, list[str]] = {}
    for category, keywords in SKILL_CATEGORIES.items():
        matches = []
        matched_spans: list[tuple[int, int]] = []
        for keyword in sorted(keywords, key=len, reverse=True):
            pattern = r"(?<![A-Za-z0-9])" + re.escape(keyword) + r"(?![A-Za-z0-9])"
            match = re.search(pattern, text, re.IGNORECASE)
            if not match:
                continue
            # Skip if this match sits entirely inside a span already claimed by a
            # longer keyword (e.g. "Node" inside an already-matched "Node.js").
            if any(start <= match.start() and match.end() <= end for start, end in matched_spans):
                continue
            matches.append(keyword)
            matched_spans.append((match.start(), match.end()))
        if matches:
            found[category] = matches
    return found


def structure_resume(text: str) -> dict:
    """Produce the full structured JSON for a resume's raw text."""
    sections = split_into_sections(text)

    return {
        "contact": extract_contact_info(text),
        "skills": extract_skills(text),
        "education": sections.get("education", []),
        "experience": sections.get("experience", []),
        "internships": sections.get("internships", []),
        "projects": sections.get("projects", []),
        "certifications": sections.get("certifications", []),
        "achievements": sections.get("achievements", []),
        "summary": " ".join(sections.get("summary", [])) or None,
    }
