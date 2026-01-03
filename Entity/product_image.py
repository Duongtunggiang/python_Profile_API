from pydantic import BaseModel
from typing import Optional


class CreateProductImageRequest(BaseModel):
    product_id: str
    image_url: str
    description: Optional[str] = None


class UpdateProductImageRequest(BaseModel):
    image_url: Optional[str] = None
    description: Optional[str] = None

