from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import date


class UpdateProfileRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    cover_url: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    hometown: Optional[str] = None
    marital_status: Optional[str] = None
    date_of_birth: Optional[date] = None  # Format: "YYYY-MM-DD" (date type)
    extra: Optional[Dict[str, Any]] = None

