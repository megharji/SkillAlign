from sqlalchemy import Column, Integer, String, DateTime,Text,ForeignKey
from app.common.config import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class JobDescriptions(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True,index=True)
    job_role = Column(String, nullable=False)
    job_description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    resumes = relationship("Resume", back_populates="job")


class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True,index=True)
    job_id = Column(
        Integer,
        ForeignKey("job_descriptions.id", ondelete="CASCADE"),
        nullable=False
    )
    file_name = Column(String, nullable=False)
    resume_text = Column(Text, nullable=False)

    match_score = Column(Integer)  # 0–100
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("JobDescriptions", back_populates="resumes")

