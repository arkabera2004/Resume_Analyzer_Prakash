"""Analysis persistence routes — save, list, view, delete, compare, and export
saved analyses."""
import re

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response

from app.database import get_analyses_collection
from app.models.analysis import AnalysisModel
from app.models.user import UserModel
from app.schemas.analysis import (
    AnalysisDetail,
    AnalysisSummary,
    CompareAnalysesRequest,
    CompareAnalysesResponse,
    SaveAnalysisRequest,
)
from app.services.analysis_serializers import compute_comparison, doc_to_detail, doc_to_summary
from app.services.report_service import build_analysis_report
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/save", response_model=AnalysisDetail, status_code=status.HTTP_201_CREATED)
async def save_analysis(
    payload: SaveAnalysisRequest,
    current_user: UserModel = Depends(get_current_user),
):
    analysis = AnalysisModel(user_id=current_user.id, **payload.model_dump())
    analyses = get_analyses_collection()
    result = await analyses.insert_one(analysis.model_dump(by_alias=True, exclude={"id"}))

    saved = await analyses.find_one({"_id": result.inserted_id})
    return doc_to_detail(saved)


@router.post("/compare", response_model=CompareAnalysesResponse)
async def compare_analyses(
    payload: CompareAnalysesRequest,
    current_user: UserModel = Depends(get_current_user),
):
    if payload.analysis_id_a == payload.analysis_id_b:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Choose two different analyses to compare."
        )

    doc_1 = await get_owned_analysis_or_404(payload.analysis_id_a, current_user.id)
    doc_2 = await get_owned_analysis_or_404(payload.analysis_id_b, current_user.id)

    # Always diff older -> newer, regardless of the order the caller passed them in,
    # so "improvement" consistently means "the more recent one got better."
    older, newer = (doc_1, doc_2) if doc_1["created_at"] <= doc_2["created_at"] else (doc_2, doc_1)
    return compute_comparison(older, newer)


@router.get("/history", response_model=list[AnalysisSummary])
async def get_history(
    limit: int = Query(default=50, ge=1, le=200),
    current_user: UserModel = Depends(get_current_user),
):
    analyses = get_analyses_collection()
    cursor = analyses.find({"user_id": current_user.id}).sort("created_at", -1).limit(limit)
    docs = await cursor.to_list(length=limit)
    return [doc_to_summary(doc) for doc in docs]


async def get_owned_analysis_or_404(analysis_id: str, user_id) -> dict:
    try:
        object_id = ObjectId(analysis_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")

    analyses = get_analyses_collection()
    doc = await analyses.find_one({"_id": object_id, "user_id": user_id})
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")
    return doc


@router.get("/{analysis_id}", response_model=AnalysisDetail)
async def get_analysis(analysis_id: str, current_user: UserModel = Depends(get_current_user)):
    doc = await get_owned_analysis_or_404(analysis_id, current_user.id)
    return doc_to_detail(doc)


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(analysis_id: str, current_user: UserModel = Depends(get_current_user)):
    await get_owned_analysis_or_404(analysis_id, current_user.id)
    analyses = get_analyses_collection()
    await analyses.delete_one({"_id": ObjectId(analysis_id)})


def _safe_filename(resume_name: str) -> str:
    stem = re.sub(r"\.(pdf|docx?)$", "", resume_name, flags=re.IGNORECASE)
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip("-") or "resume"
    return f"{stem}-analysis-report.pdf"


@router.get("/{analysis_id}/report")
async def download_report(analysis_id: str, current_user: UserModel = Depends(get_current_user)):
    doc = await get_owned_analysis_or_404(analysis_id, current_user.id)
    pdf_bytes = build_analysis_report(doc)
    filename = _safe_filename(doc["resume_name"])

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
