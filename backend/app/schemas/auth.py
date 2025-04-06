from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from backend.app.schemas.base import BaseSchema, BaseResponseSchema


class RoleBase(BaseSchema):
    """Base schema for Role"""

    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    """Schema for creating a new role"""

    pass


class RoleUpdate(RoleBase):
    """Schema for updating a role"""

    name: Optional[str] = None


class RoleResponse(RoleBase, BaseResponseSchema):
    """Schema for role response"""

    pass


class UserBase(BaseSchema):
    """Base schema for User"""

    username: str
    email: EmailStr
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating a new user"""

    password: str = Field(..., min_length=8)
    role_ids: List[int] = []


class UserLogin(BaseSchema):
    """Schema for user login"""

    username: str
    password: str


class UserUpdate(BaseSchema):
    """Schema for updating a user"""

    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    role_ids: Optional[List[int]] = None


class UserResponse(UserBase, BaseResponseSchema):
    """Schema for user response"""

    roles: List[RoleResponse] = []


class Token(BaseSchema):
    """Schema for authentication token"""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseSchema):
    """Schema for token data"""

    username: Optional[str] = None
    scopes: List[str] = []


class PasswordReset(BaseSchema):
    """Schema for password reset"""

    email: EmailStr


class PasswordChange(BaseSchema):
    """Schema for password change"""

    old_password: str
    new_password: str = Field(..., min_length=8)
