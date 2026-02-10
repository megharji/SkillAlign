from fastapi import APIRouter, Form, UploadFile, File, Depends,HTTPException
from typing import List
import logging

from app.common.token_utils import get_current_user
from app.common.resume_utils import extract_resume_text,get_color_code, get_match_level,calculate_ats_score

logger = logging.getLogger(__name__)

hr_routers = APIRouter()


@hr_routers.post("/score-resumes")
async def score_resumes(
    jd_text: str = Form(...),
    resumes: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "HR":
        raise HTTPException(status_code=403, detail="Only HR can use this endpoint")

    results = []

    for resume in resumes:
        resume_text = await extract_resume_text(resume)
        raw_score = calculate_ats_score(resume_text, jd_text)  # 0–1
        score = round(raw_score * 10, 1)  # 0–10

        results.append({
            "file_name": resume.filename,
            "score": score,
            "match_level": get_match_level(score),
            "color_code": get_color_code(score)
        })

   
    results.sort(key=lambda x: x["score"], reverse=True)

    strong_matches = [r for r in results if r["score"] >= 8]
    potential_matches = [r for r in results if 6 <= r["score"] < 8]
    rejected = [r for r in results if r["score"] < 6]

    # shortlist: first take all strong, then fill from potential (max 10)
    shortlisted = (strong_matches + potential_matches)[:10]

    # others: remaining potential + rejected (exclude shortlisted)
    shortlisted_set = {(r["file_name"], r["score"]) for r in shortlisted}
    others = [r for r in (potential_matches + rejected) if (r["file_name"], r["score"]) not in shortlisted_set]

    return {
        "user_id": current_user.get("user_id"),
        "total_resumes": len(results),
        "summary": {
            "strong_matches": len(strong_matches),
            "potential_matches": len(potential_matches),
            "rejected": len(rejected),
        },
        "shortlisted": shortlisted,
        "others": others,
    }
