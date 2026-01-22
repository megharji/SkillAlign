from sklearn.metrics.pairwise import cosine_similarity
from app.common.embedding import model
import io
from PyPDF2 import PdfReader
from docx import Document

def calculate_ats_score(resume_text: str, jd_text: str) -> float:
    if not resume_text or not jd_text:
        return 0.0

    jd_vec = model.encode([jd_text])
    resume_vec = model.encode([resume_text])

    score = cosine_similarity(jd_vec, resume_vec)[0][0]
    return round(float(score), 3)



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
    if score >= 0.8:
        return "Excellent Match"
    elif score >= 0.6:
        return "Good Match"
    elif score >= 0.4:
        return "Average Match"
    else:
        return "Poor Match"

