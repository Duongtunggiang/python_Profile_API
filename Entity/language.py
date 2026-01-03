from pydantic import BaseModel
from typing import Optional


class CreateLanguageRequest(BaseModel):
    language: str
    level: str


class UpdateLanguageRequest(BaseModel):
    language: Optional[str] = None
    level: Optional[str] = None

