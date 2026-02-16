# from sklearn.metrics.pairwise import cosine_similarity
import math
import io
from app.common.embedding import get_model
from PyPDF2 import PdfReader
from docx import Document

# def calculate_ats_score(resume_text: str, jd_text: str) -> float:
#     if not resume_text or not jd_text:
#         return 0.0
#     model = get_model()
#     jd_vec = model.encode([jd_text])
#     resume_vec = model.encode([resume_text])

#     score = cosine_similarity(jd_vec, resume_vec)[0][0]
#     return round(float(score), 3)

def _cosine(a, b) -> float:
    dot = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(y*y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

def calculate_ats_score(resume_text: str, jd_text: str) -> float:
    if not resume_text or not jd_text:
        return 0.0

    model = get_model()
    jd_vec = model.encode([jd_text])[0]
    resume_vec = model.encode([resume_text])[0]

    score01 = _cosine(jd_vec, resume_vec)   # 0..1
    score10 = score01 * 10                  # 0..10
    return round(float(score10), 2)

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
