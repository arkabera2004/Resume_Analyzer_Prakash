"""Curated word lists used by the deterministic ATS scoring engine.

Kept separate from skill_taxonomy.py because these lists serve a different purpose:
skill_taxonomy identifies *what* technologies are mentioned, these lists judge *how*
the resume is written (strong vs. weak phrasing).
"""

# Bullet points that open with a strong action verb read as achievement-oriented
# rather than passive ("Responsible for...") — a well-documented ATS/recruiter
# heuristic. Not exhaustive; a reasonable, defensible sample.
STRONG_ACTION_VERBS = {
    "achieved", "accelerated", "administered", "analyzed", "architected", "automated",
    "built", "collaborated", "created", "delivered", "deployed", "designed",
    "developed", "devised", "directed", "engineered", "enhanced", "established",
    "executed", "expanded", "generated", "implemented", "improved", "increased",
    "initiated", "integrated", "launched", "led", "managed", "mentored",
    "migrated", "optimized", "orchestrated", "organized", "pioneered", "planned",
    "produced", "programmed", "reduced", "refactored", "resolved", "scaled",
    "shipped", "spearheaded", "streamlined", "strengthened", "supervised",
    "tested", "trained", "transformed", "upgraded",
}

# Vague, passive, or filler phrases that weaken a bullet point and that many ATS/
# recruiter checklists flag explicitly.
WEAK_PHRASES = [
    "responsible for",
    "worked on",
    "helped with",
    "duties included",
    "team player",
    "hard worker",
    "detail oriented",
    "detail-oriented",
    "go-getter",
    "think outside the box",
    "results-driven individual",
    "highly motivated",
]
