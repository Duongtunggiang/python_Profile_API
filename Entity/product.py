from pydantic import BaseModel
from typing import Optional


class CreateProductRequest(BaseModel):
    product_name: str
    product_url: Optional[str] = None
    product_image: Optional[str] = None


class UpdateProductRequest(BaseModel):
    product_name: Optional[str] = None
    product_url: Optional[str] = None
    product_image: Optional[str] = None

