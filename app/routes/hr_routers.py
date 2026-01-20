from fastapi import APIRouter, Depends, HTTPException, Body, Depends,UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.hr_schema import AddJobDescription,UploadResumeResponse
from app.models.hr_model import JobDescriptions,Resume
from app.common.token_utils import get_current_user
from app.common.response_utils import ResponseModel, Http_Exception
import logging
from typing import Any, List, Optional
import io
from PyPDF2 import PdfReader
from docx import Document
import io
from app.common.resume_utils import extract_resume_text,calculate_match_score
logger = logging.getLogger(__name__)

hr_routers = APIRouter()

@hr_routers.post("/create_jd")
def create_jd(
    param: AddJobDescription,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        # role check
        if current_user["role"] != "HR":
            raise HTTPException(
                status_code=403,
                detail="Only HR can create Job Descriptions"
            )

        new_jd = JobDescriptions(
            job_role=param.job_role,
            job_description=param.job_description,
        )

        db.add(new_jd)
        db.commit()
        db.refresh(new_jd)

        return ResponseModel(
            status_code=201,
            status="success",
            message="Job Description created successfully",
            payload=new_jd
        )

    except HTTPException:
        raise

    except Exception as exp:
        db.rollback()
        logger.error(f"Error in creating JD: {str(exp)}")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )



@hr_routers.post("/upload_resumes", response_model=List[UploadResumeResponse])
async def upload_resumes(
    job_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload multiple resumes for a specific Job Description.
    Extracts text for future matching.
    """

    # Role check
    if current_user["role"] != "HR":
        raise HTTPException(
            status_code=403,
            detail="Only HR can upload resumes"
        )

    # Check job exists
    job = db.query(JobDescriptions).filter(JobDescriptions.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job Description not found")

    saved_resumes = []

    for file in files:
        try:
            # Extract text from PDF/DOCX using the helper function
            resume_text = await extract_resume_text(file)
            
            # Skip files that couldn't be extracted
            if not resume_text.strip():
                logger.warning(f"Skipping file {file.filename}, no text extracted.")
                continue

            new_resume = Resume(
                job_id=job_id,
                file_name=file.filename,
                resume_text=resume_text,
                match_score=calculate_match_score(resume_text, job.job_description)
            )

            db.add(new_resume)
            db.commit()
            db.refresh(new_resume)

            saved_resumes.append(new_resume)

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to process file {file.filename}: {str(e)}")
            continue  # skip failed file, process others

    if not saved_resumes:
        raise HTTPException(status_code=400, detail="No resumes were uploaded successfully")

    return saved_resumes