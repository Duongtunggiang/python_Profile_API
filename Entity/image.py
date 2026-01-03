from pydantic import BaseModel
from typing import Optional


class CreateImageRequest(BaseModel):
    images_url: str
    image_type: str


class UpdateImageRequest(BaseModel):
    images_url: Optional[str] = None
    image_type: Optional[str] = None

