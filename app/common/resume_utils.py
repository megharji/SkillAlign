# from sklearn.metrics.pairwise import cosine_similarity
import math
import io
from app.common.embedding import get_similarity
from PyPDF2 import PdfReader
from docx import Document

def calculate_ats_score(resume_text: str, jd_text: str) -> float:
    if not resume_text or not jd_text:
        return 0.0

    score01 = get_similarity(jd_text, [resume_text])[0] 

    score10 = score01 * 10   
    return round(score10, 2)


async def extract_resume_text(file):
    contents = await file.read()
    ext = file.filename.split('.')[-1].lower()

    if ext == "pdf":
        reader = PdfReader(io.BytesIO(contents))
        return " ".join(
            page.extract_text() or "" for page in reader.pages
        ).strip()

    elif ext == "docx":
        doc = Document(io.BytesIO(contents))
        return " ".join(p.text for p in doc.paragraphs).strip()

    else:
        return ""

def get_match_level(score: float) -> str:
    if score >= 8:
        return "Excellent Match"
    elif score >= 6:
        return "Potential Match"
    else:
        return "Rejected"


def get_color_code(score: float):
    if score >= 8:
        return "GREEN"
    elif score >= 6:
        return "YELLOW"
    return "RED"
