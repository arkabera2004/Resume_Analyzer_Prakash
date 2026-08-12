"""Dashboard aggregate-stats route."""
from fastapi import APIRouter, Depends

from app.database import get_analyses_collection
from app.models.user import UserModel
from app.schemas.analysis import DashboardStats
from app.services.analysis_serializers import doc_to_summary
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

RECENT_ANALYSES_LIMIT = 5


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(current_user: UserModel = Depends(get_current_user)):
    analyses = get_analyses_collection()
    cursor = analyses.find({"user_id": current_user.id}).sort("created_at", -1)
    docs = await cursor.to_list(length=None)

    if not docs:
        return DashboardStats(
            total_analyses=0,
            best_ats_score=None,
            avg_match_score=None,
            unique_skills_count=0,
            recent_analyses=[],
        )

    ats_scores = [doc["ats_score"] for doc in docs if doc.get("ats_score") is not None]
    match_scores = [doc["match_score"] for doc in docs if doc.get("match_score") is not None]

    unique_skills: set[str] = set()
    for doc in docs:
        parsed_skills = doc.get("parsed_resume", {}).get("skills", {})
        for skill_list in parsed_skills.values():
            unique_skills.update(skill_list)

    return DashboardStats(
        total_analyses=len(docs),
        best_ats_score=max(ats_scores) if ats_scores else None,
        avg_match_score=round(sum(match_scores) / len(match_scores)) if match_scores else None,
        unique_skills_count=len(unique_skills),
        recent_analyses=[doc_to_summary(doc) for doc in docs[:RECENT_ANALYSES_LIMIT]],
    )
