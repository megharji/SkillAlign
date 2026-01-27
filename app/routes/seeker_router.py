
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import requests
import os

from app.common.resume_utils import extract_resume_text

seeker_router = APIRouter()

HF_TOKEN = os.getenv("HF_TOKEN")  # token hardcode mat kar
HF_URL = "https://router.huggingface.co/v1/chat/completions"


headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}


@seeker_router.post("/compare-resume-jd")
async def compare_resume_jd(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...)
):
    
    # ---- 1. Resume text extract ----
    try:
        resume_text = await extract_resume_text(resume_file)


    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Resume extraction failed: {str(e)}")

    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Empty resume text after extraction")

    # ---- 2. Prompt ----
    prompt = f"""
You are an expert ATS and HR resume evaluator.

Compare the RESUME with the JOB DESCRIPTION and analyze strictly.

TASKS:
1. List missing skills (skills present in JD but absent in resume)
2. List matched skills
3. Give improvement suggestions
4. Give overall suitability percentage (0–100%)

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Return response in clear bullet points.
"""

    payload = {
        "model": "openai/gpt-oss-20b:groq",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
        # remove max_new_tokens completely
    }


    response = requests.post(HF_URL, headers=headers, json=payload, timeout=60)

    if response.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=f"HuggingFace error: {response.text}"
        )

    result = response.json()
    ai_text = result["choices"][0]["message"]["content"]

    return {
        "status": "success",
        "analysis": ai_text
    }





