from pydantic import BaseModel, Field,ConfigDict
from typing import Optional
from datetime import datetime

class AddJobDescription(BaseModel):
    id: Optional[int] = Field(example=1, default=None)
    job_role: str = Field(description="Job role", example="Backend Developer")
    job_description: str = Field(
        description="Full job description text",
        example="We are looking for a Backend Developer with experience in Python, FastAPI, SQL..."
    )  
    model_config = {
        "from_attributes": True  # replaces orm_mode
    }


class UploadResumeResponse(BaseModel):
    id: int = Field(..., description="Resume ID in database")
    job_id: int = Field(..., description="ID of the Job Description this resume belongs to")
    file_name: str = Field(..., description="Original filename of the uploaded resume")

    model_config = {
        "from_attributes": True  # replaces orm_mode
    }