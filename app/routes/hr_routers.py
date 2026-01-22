from fastapi import APIRouter, Form, UploadFile, File, Depends
from typing import List
import logging

from app.common.token_utils import get_current_user
from app.common.resume_utils import extract_resume_text, get_match_level,calculate_ats_score

logger = logging.getLogger(__name__)

hr_routers = APIRouter()


@hr_routers.post("/match-resumes")
async def match_resumes(
    jd_text: str = Form(...),
    resumes: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user)
):
    print("Current User:", current_user)
    results = []

    for resume in resumes:
        resume_text = await extract_resume_text(resume)
        raw_score = calculate_ats_score(resume_text, jd_text)

        match_level = get_match_level(raw_score)

        results.append({
            "file_name": resume.filename,
            "score": round(raw_score * 10, 1),
            "match_level": match_level
        })

    return {
        "user_id": current_user.get("user_id"),
        "total_resumes": len(resumes),
        "results": results
    }