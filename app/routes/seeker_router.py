from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
import requests
import os
import json
import re

from app.common.resume_utils import extract_resume_text
from app.common.token_utils import get_current_user

seeker_router = APIRouter()

HF_TOKEN = os.getenv("HF_TOKEN")
HF_URL = os.getenv("HF_URL")

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}


def extract_json(text: str):
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise ValueError("No JSON object found")
        return json.loads(match.group())



@seeker_router.post("/compare-resume-jd")
async def compare_resume_jd(
    resume_file: UploadFile = File(...),

    jd_1: str = Form(...),
    jd_2: str = Form(None),
    jd_3: str = Form(None),
    jd_4: str = Form(None),
    jd_5: str = Form(None),

    current_user: dict = Depends(get_current_user)
):
    # ---- AUTH ----
    if current_user.get("role") != "Seeker":
        raise HTTPException(status_code=403, detail="Only Seekers can use this endpoint")

    # ---- RESUME TEXT ----
    try:
        resume_text = await extract_resume_text(resume_file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Resume extraction failed: {str(e)}")

    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Empty resume text")

    # ---- VALIDATE + COLLECT JDs (keep original jd_number 1..5) ----
    jd_inputs = [jd_1, jd_2, jd_3, jd_4, jd_5]

    valid_jds = []
    for idx, jd in enumerate(jd_inputs, start=1):
        if jd and jd.strip() and jd.strip().lower() != "string":
            valid_jds.append((idx, jd.strip()))

    if not valid_jds:
        raise HTTPException(status_code=400, detail="At least one JD is required")

    results = []

    # ---- LOOP OVER ONLY FILLED JDs ----
    for idx, jd in valid_jds:
        prompt = f"""
You are an ATS-grade resume evaluator.

IMPORTANT RULES:
- Treat project descriptions as valid proof of skills.
- Treat synonyms as the same skill.
- Do NOT list same skill in matched & missing.

SCORING RULES:
- Required skills > Nice to have
- Missing required skills reduces score heavily
- Experience gap must reduce score

OUTPUT JSON ONLY:
{{
  "missing_skills": [string],
  "matched_skills": [string],
  "improvement_suggestions": [string],
  "suitability_percentage": number
}}

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd}
"""

        payload = {
            "model": "openai/gpt-oss-20b:groq",
            "messages": [
                {"role": "system", "content": "Return ONLY valid JSON"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }

        parsed = {
            "missing_skills": [],
            "matched_skills": [],
            "improvement_suggestions": [],
            "suitability_percentage": 0
        }

        try:
            response = requests.post(HF_URL, headers=headers, json=payload, timeout=60)

            if response.status_code == 200:
                ai_content = response.json()["choices"][0]["message"]["content"]
                parsed = extract_json(ai_content)
        except Exception:
            # keep default parsed (zeros) on any failure
            pass

        results.append({
            "jd_number": idx,
            "analysis": parsed
        })

    if not results:
        raise HTTPException(status_code=500, detail="AI failed for all JDs")

    # ---- BEST MATCH ----
    best_match = max(
        results,
        key=lambda x: x["analysis"].get("suitability_percentage", 0)
    )

    # ---- RESPONSE ----
    return {
        "status": "success",
        "total_jds_compared": len(valid_jds),  # ✅ now correct
        "best_matching_jd": best_match,
        "all_jd_results": results  # ✅ only filled JDs
    }