"""Converts a raw `analyses` MongoDB document into API response schemas, and
computes the diff between two saved analyses for the compare feature.

Shared between routes/analysis.py and routes/dashboard.py so both stay in sync
about what a saved analysis looks like.
"""
from app.schemas.analysis import AnalysisSummary, CompareAnalysesResponse, AnalysisDetail


def doc_to_summary(doc: dict) -> AnalysisSummary:
    return AnalysisSummary(
        id=str(doc["_id"]),
        resume_name=doc["resume_name"],
        job_title=doc.get("job_title"),
        ats_score=doc.get("ats_score"),
        match_score=doc.get("match_score"),
        created_at=doc["created_at"],
    )


def doc_to_detail(doc: dict) -> AnalysisDetail:
    return AnalysisDetail(
        id=str(doc["_id"]),
        resume_name=doc["resume_name"],
        job_title=doc.get("job_title"),
        ats_score=doc.get("ats_score"),
        match_score=doc.get("match_score"),
        created_at=doc["created_at"],
        parsed_resume=doc.get("parsed_resume", {}),
        keyword_score=doc.get("keyword_score"),
        skills_score=doc.get("skills_score"),
        structure_score=doc.get("structure_score"),
        experience_score=doc.get("experience_score"),
        project_score=doc.get("project_score"),
        formatting_score=doc.get("formatting_score"),
        matching_skills=doc.get("matching_skills", []),
        missing_skills=doc.get("missing_skills", []),
        matching_keywords=doc.get("matching_keywords", []),
        missing_keywords=doc.get("missing_keywords", []),
        experience_relevance=doc.get("experience_relevance"),
        project_relevance=doc.get("project_relevance"),
        section_scores=doc.get("section_scores", {}),
        strengths=doc.get("strengths", []),
        weaknesses=doc.get("weaknesses", []),
        priority_improvements=doc.get("priority_improvements", []),
        recommended_roles=doc.get("recommended_roles", []),
        recommendations=doc.get("recommendations", []),
    )


def _flatten_skills(doc: dict) -> set[str]:
    parsed_skills = doc.get("parsed_resume", {}).get("skills", {})
    return {skill for skills in parsed_skills.values() for skill in skills}


def compute_comparison(doc_a: dict, doc_b: dict) -> CompareAnalysesResponse:
    """Diff two saved analyses. Callers must pass `doc_a` as the older one (by
    created_at) so score deltas and new/removed sets consistently read as a -> b."""
    skills_a, skills_b = _flatten_skills(doc_a), _flatten_skills(doc_b)
    keywords_a = set(doc_a.get("matching_keywords", []))
    keywords_b = set(doc_b.get("matching_keywords", []))

    sections_a = doc_a.get("section_scores", {})
    sections_b = doc_b.get("section_scores", {})
    improved_sections = []
    regressed_sections = []
    for key in set(sections_a) | set(sections_b):
        score_a = sections_a.get(key, {}).get("score")
        score_b = sections_b.get(key, {}).get("score")
        if score_a is None or score_b is None:
            continue
        if score_b > score_a:
            improved_sections.append(key)
        elif score_b < score_a:
            regressed_sections.append(key)

    ats_a, ats_b = doc_a.get("ats_score"), doc_b.get("ats_score")
    match_a, match_b = doc_a.get("match_score"), doc_b.get("match_score")

    return CompareAnalysesResponse(
        analysis_a=doc_to_summary(doc_a),
        analysis_b=doc_to_summary(doc_b),
        ats_score_change=(ats_b - ats_a) if ats_a is not None and ats_b is not None else None,
        match_score_change=(
            (match_b - match_a) if match_a is not None and match_b is not None else None
        ),
        new_skills=sorted(skills_b - skills_a),
        removed_skills=sorted(skills_a - skills_b),
        new_keywords=sorted(keywords_b - keywords_a),
        removed_keywords=sorted(keywords_a - keywords_b),
        improved_sections=sorted(improved_sections),
        regressed_sections=sorted(regressed_sections),
    )
