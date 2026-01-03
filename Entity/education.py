from pydantic import BaseModel
from typing import Optional
from datetime import date


class CreateEducationRequest(BaseModel):
    school_name: str
    start_year: Optional[date] = None  # Format: "YYYY-MM-DD" (date type)
    end_year: Optional[date] = None  # Format: "YYYY-MM-DD" (date type)
    description: Optional[str] = None


class UpdateEducationRequest(BaseModel):
    school_name: Optional[str] = None
    start_year: Optional[date] = None  # Format: "YYYY-MM-DD" (date type)
    end_year: Optional[date] = None  # Format: "YYYY-MM-DD" (date type)
    description: Optional[str] = None

