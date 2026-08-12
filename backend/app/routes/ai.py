"""AI-generated recommendation routes."""
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.user import UserModel
from app.schemas.ai import (
    AIRecommendationsRequest,
    AIRecommendationsResponse,
    ImproveBulletRequest,
    ImproveBulletResponse,
)
from app.services.ai_service import AIServiceError
from app.services.bullet_improver import improve_bullet
from app.services.recommendation_service import get_ai_recommendations
from app.services.resume_structurer import structure_resume
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/recommendations", response_model=AIRecommendationsResponse)
async def recommendations(
    payload: AIRecommendationsRequest,
    _current_user: UserModel = Depends(get_current_user),
):
    resume_text = payload.resume_text.strip()
    if not resume_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No resume text provided.")

    parsed_resume = structure_resume(resume_text)

    try:
        result = get_ai_recommendations(resume_text, parsed_resume)
    except AIServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    return AIRecommendationsResponse(**result)


@router.post("/improve-bullet", response_model=ImproveBulletResponse)
async def improve_bullet_route(
    payload: ImproveBulletRequest,
    _current_user: UserModel = Depends(get_current_user),
):
    bullet_text = payload.bullet_text.strip()
    if not bullet_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No bullet text provided.")

    try:
        result = improve_bullet(bullet_text, payload.context)
    except AIServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    return ImproveBulletResponse(**result)
