from pydantic import BaseModel
from typing import Optional

class CreateTargetRequest(BaseModel):
    target: str

class UpdateTargetRequest(BaseModel):
    target: Optional[str] = None

