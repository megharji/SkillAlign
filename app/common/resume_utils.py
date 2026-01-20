import io
from PyPDF2 import PdfReader
from docx import Document
from fastapi import UploadFile

async def extract_resume_text(file: UploadFile) -> str:
    contents = await file.read()
    ext = file.filename.split('.')[-1].lower()
    
    if ext == "pdf":
        try:
            reader = PdfReader(io.BytesIO(contents))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except:
            return ""
    elif ext == "docx":
        try:
            doc = Document(io.BytesIO(contents))
            text = "\n".join([p.text for p in doc.paragraphs])
            return text.strip()
        except:
            return ""
    else:
        # fallback
        return contents.decode("utf-8", errors="ignore")

def calculate_match_score(resume_text: str, jd_text: str) -> int:
    jd_words = set(jd_text.lower().split())
    resume_words = set(resume_text.lower().split())
    if not jd_words:
        return 0
    matched_words = jd_words & resume_words
    score = round(len(matched_words) / len(jd_words) * 10, 1)
    return min(score, 100)
