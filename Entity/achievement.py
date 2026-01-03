from pydantic import BaseModel
from typing import Optional


class CreateAchievementRequest(BaseModel):
    achievement_name: str
    description: Optional[str] = None


class UpdateAchievementRequest(BaseModel):
    achievement_name: Optional[str] = None
    description: Optional[str] = None

