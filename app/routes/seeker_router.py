from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from typing import List
import logging

from app.common.token_utils import get_current_user
from app.common.resume_utils import extract_resume_text
from app.common.text_generation import get_text_generator
from app.common.config import HF_TEXT_MODEL

logger = logging.getLogger(__name__)

seeker_router = APIRouter()


@seeker_router.post("/resume-review")
async def resume_review(
    jd_text: str = Form(...),
    resume_file: UploadFile = File(...)
):
    """
    Resume review using Hugging Face model downloaded from Hub.
    Models are automatically downloaded from Hugging Face Hub on first use.
    """
    try:
        resume_text = await extract_resume_text(resume_file)

        if not resume_text:
            raise HTTPException(status_code=400, detail="Resume text extraction failed")

        prompt = f"""
You are an expert ATS and resume reviewer.

JOB DESCRIPTION:
<<<
{jd_text}
>>>

RESUME:
<<<
{resume_text}
>>>

TASKS:
1. Give an overall match score (0–10)
2. Mention 3 strengths
3. Mention 3 missing or weak areas
4. Suggest concrete improvements
"""

        # Get generator - model will be downloaded from Hugging Face Hub automatically
        generator = get_text_generator(model_name=HF_TEXT_MODEL)
        
        review = generator.generate(
            prompt=prompt,
            max_new_tokens=300,
            temperature=0.4,
            repetition_penalty=1.2
        )

        return {
            "success": True,
            "review": review,
            "model": HF_TEXT_MODEL
        }
        
    except Exception as e:
        logger.error(f"Resume review error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Resume review failed: {str(e)}")
