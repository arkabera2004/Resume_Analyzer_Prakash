"""Job description analysis routes."""
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.user import UserModel
from app.schemas.job import JobAnalyzeRequest, JobDescriptionAnalysis
from app.services.jd_analyzer import analyze_job_description
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/job", tags=["job"])


@router.post("/analyze", response_model=JobDescriptionAnalysis)
async def analyze_job(
    payload: JobAnalyzeRequest,
    _current_user: UserModel = Depends(get_current_user),
):
    text = payload.job_description.strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No job description provided."
        )

    return JobDescriptionAnalysis(**analyze_job_description(text))
