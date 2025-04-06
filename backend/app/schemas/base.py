from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class BaseSchema(BaseModel):
    """Base schema with ORM mode enabled"""

    model_config = ConfigDict(from_attributes=True)


class TimestampSchema(BaseSchema):
    """Schema with created_at and updated_at fields"""

    created_at: datetime
    updated_at: datetime


class BaseResponseSchema(BaseSchema):
    """Base response schema with ID and timestamps"""

    id: int
    created_at: datetime
    updated_at: datetime


class PaginatedResponse(BaseSchema):
    """Base schema for paginated responses"""

    items: list
    total: int
    page: int
    size: int
    pages: int


class StatusMessage(BaseSchema):
    """Schema for status messages"""

    status: str
    message: str
