from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class APIKeyBase(BaseModel):
    description: Optional[str] = None
    is_active: bool = True

class APIKeyCreate(APIKeyBase):
    pass

class APIKeyResponse(APIKeyBase):
    id: str
    key: Optional[str] = Field(None, description="The raw API key, only returned upon creation.")
    created_at: datetime

    class Config:
        from_attributes = True
