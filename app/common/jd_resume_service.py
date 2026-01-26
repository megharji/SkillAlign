from app.common.resume_utils import calculate_ats_score, get_match_level
from app.common.resume_summary_utils import get_summary
import asyncio

async def analyze_resume(resume_text: str, jd_text: str) -> dict:
    """
    Returns:
    {
        "score": float,
        "match_level": str,
        "summary": str
    }
    """
    # 1️⃣ Calculate ATS score
    score = calculate_ats_score(resume_text, jd_text)
    match_level = get_match_level(score)

    # 2️⃣ Get human-readable summary
    # If you want async, wrap in executor to avoid blocking
    loop = asyncio.get_event_loop()
    summary = await loop.run_in_executor(None, get_summary, resume_text, jd_text)

    return {
        "score": score,
        "match_level": match_level,
        "summary": summary
    }
