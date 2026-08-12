"""Keyword lists specific to job-description analysis.

Separate from skill_taxonomy.py (which is technology-focused) — these cover
methodology/process terms and degree phrasing commonly found in job postings.
"""

# Methodology, architecture, and process terms that commonly appear as JD keywords
# alongside specific technologies. Matched the same way as skill_taxonomy entries
# (case-insensitive, word-boundary-aware).
GENERAL_KEYWORDS = [
    "Agile", "Scrum", "Kanban", "CI/CD", "Microservices", "Cloud", "DevOps",
    "REST API", "API", "Unit Testing", "TDD", "Object-Oriented Programming", "OOP",
    "Data Structures", "Algorithms", "System Design", "Cross-functional",
    "Version Control", "Code Review", "Distributed Systems", "Machine Learning",
    "Data Analysis",
]

# Checked longest-first, same pattern as skill matching — e.g. "Bachelor's degree"
# is preferred over the bare "Bachelor" it contains.
DEGREE_PHRASES = [
    "Bachelor's degree", "Bachelor of Science", "Bachelor of Engineering",
    "Bachelor of Technology", "Master's degree", "Master of Science",
    "Master of Business Administration", "Associate's degree", "Ph.D.", "PhD",
    "Doctorate", "B.Tech", "M.Tech", "MBA", "B.E.", "M.E.", "B.Sc", "M.Sc",
    "Bachelor", "Master",
]

# Ordered so more specific phrasing ("X+ years") is tried before generic "years".
EXPERIENCE_PATTERNS = [
    r"\d+\s*[-–to]+\s*\d+\+?\s*years?(?:\s+of\s+experience)?",
    r"\d+\+?\s*years?(?:\s+of\s+experience)?",
    r"minimum\s+of\s+\d+\+?\s*years?",
    r"at\s+least\s+\d+\+?\s*years?",
]
