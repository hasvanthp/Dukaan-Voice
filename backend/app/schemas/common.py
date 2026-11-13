from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class APIError(BaseModel):
    detail: str


class UserContext(BaseModel):
    user_id: UUID
    store_id: UUID


class BaseResponse(BaseModel):
    success: bool = True
    timestamp: datetime = Field(default_factory=datetime.utcnow)
