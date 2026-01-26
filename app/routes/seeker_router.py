from fastapi import APIRouter, Form, UploadFile, File, Depends,HTTPException
from typing import List
import logging
from app.common.jd_resume_service import analyze_resume
from app.common.token_utils import get_current_user
from app.common.resume_utils import extract_resume_text, get_match_level,calculate_ats_score

import asyncio
from pydantic import BaseModel

logger = logging.getLogger(__name__)

seeker_router = APIRouter()

class ResumeJD(BaseModel):
    resume_text: str
    jd_text: str
    
@seeker_router.post("/match-resume")
async def analyze(data: ResumeJD):
    result = await analyze_resume(data.resume_text, data.jd_text)
    return result