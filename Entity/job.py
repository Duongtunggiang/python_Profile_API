from pydantic import BaseModel
from typing import Optional
from datetime import date


class CreateJobRequest(BaseModel):
    job_name: str
    company_name: str
    start_date: Optional[date] = None  # Format: "YYYY-MM-DD" (date type)
    end_date: Optional[str] = None  # Text type - có thể là "Now" hoặc date string
    description: Optional[str] = None


class UpdateJobRequest(BaseModel):
    job_name: Optional[str] = None
    company_name: Optional[str] = None
    start_date: Optional[date] = None  # Format: "YYYY-MM-DD" (date type)
    end_date: Optional[str] = None  # Text type - có thể là "Now" hoặc date string
    description: Optional[str] = None

