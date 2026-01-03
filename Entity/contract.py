from pydantic import BaseModel
from typing import Optional


class CreateContractRequest(BaseModel):
    contract_name: str
    status: str


class UpdateContractRequest(BaseModel):
    contract_name: Optional[str] = None
    status: Optional[str] = None

