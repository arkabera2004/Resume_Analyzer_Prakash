"""Shared longest-match-first keyword matching, used by resume and job-description
parsing so both "what skills are mentioned" checks behave identically.
"""
import re


def match_keywords(text: str, keywords: list[str]) -> list[str]:
    """Return which `keywords` appear in `text`, word-boundary-aware and case-insensitive.

    Keywords are checked longest-first so a match like "Node.js" is kept instead of
    also reporting the shorter "Node" that's a substring of it.
    """
    matches: list[str] = []
    matched_spans: list[tuple[int, int]] = []

    for keyword in sorted(keywords, key=len, reverse=True):
        pattern = r"(?<![A-Za-z0-9])" + re.escape(keyword) + r"(?![A-Za-z0-9])"
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            continue
        if any(start <= match.start() and match.end() <= end for start, end in matched_spans):
            continue
        matches.append(keyword)
        matched_spans.append((match.start(), match.end()))

    return matches
