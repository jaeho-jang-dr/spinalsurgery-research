from typing import Optional
from pydantic import BaseModel, EmailStr, UUID4
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: UserRole
    institution: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None
    institution: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDBBase(UserBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    password_hash: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None
    type: Optional[str] = None