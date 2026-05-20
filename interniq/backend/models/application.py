from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class ApplicantData(BaseModel):
    internship_year: str = "2026"
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    location: str = "PK"
    city: str
    university: str
    degree: str
    major: str
    cgpa: str
    semester: str
    class_ranking: Optional[str] = None
    field: str
    selected_tracks: List[str] = Field(default_factory=list)
    video_link: Optional[str] = None


class ApplicationRecord(ApplicantData):
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    resume_url: Optional[str] = None
    transcript_url: Optional[str] = None
    photo_url: Optional[str] = None
    status: str = "pending"
