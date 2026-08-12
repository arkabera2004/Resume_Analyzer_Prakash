"""Resume-vs-job-description matching routes."""
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.user import UserModel
from app.schemas.match import MatchAnalyzeRequest, MatchAnalyzeResponse
from app.services.jd_analyzer import analyze_job_description
from app.services.job_matcher import match_resume_to_job
from app.services.resume_structurer import structure_resume
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/match", tags=["match"])


@router.post("/analyze", response_model=MatchAnalyzeResponse)
async def analyze_match(
    payload: MatchAnalyzeRequest,
    _current_user: UserModel = Depends(get_current_user),
):
    resume_text = payload.resume_text.strip()
    job_description = payload.job_description.strip()

    if not resume_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No resume text provided.")
    if not job_description:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No job description provided."
        )

    parsed_resume = structure_resume(resume_text)
    parsed_job = analyze_job_description(job_description)
    match = match_resume_to_job(resume_text, parsed_resume, parsed_job)

    return MatchAnalyzeResponse(**match, parsed_resume=parsed_resume, parsed_job=parsed_job)
