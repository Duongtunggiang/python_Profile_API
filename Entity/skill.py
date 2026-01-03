from pydantic import BaseModel
from typing import Optional

class CreateSkillRequest(BaseModel):
    skill_name: str
    level: str

class UpdateSkillRequest(BaseModel):
    skill_name: Optional[str] = None
    level: Optional[str] = None

