"""Converts a raw `analyses` MongoDB document into API response schemas.

Shared between routes/analysis.py and routes/dashboard.py so both stay in sync
about what a saved analysis looks like.
"""
from app.schemas.analysis import AnalysisDetail, AnalysisSummary


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
