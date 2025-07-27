"""
Mock authentication for testing without database
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from app.core.security import create_access_token, get_password_hash
from app.core.config import settings
import uuid

router = APIRouter()

# Mock users (in-memory storage)
MOCK_USERS = {
    "test@example.com": {
        "email": "test@example.com",
        "password": "test1234",
        "name": "Test User",
        "id": "test-user-id",
        "role": "admin"
    }
}

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    role: str = "researcher"
    institution: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None

@router.post("/mock-login")
async def mock_login(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Mock login endpoint for testing"""
    user = MOCK_USERS.get(form_data.username)
    
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user["email"],
        expires_delta=access_token_expires
    )
    
    # Use a separate function for refresh token if available
    from app.core.security import create_refresh_token
    refresh_token = create_refresh_token(subject=user["email"])
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"]
        }
    }

@router.post("/mock-register")
async def mock_register(data: RegisterRequest):
    """Mock register endpoint for testing"""
    # Check if user already exists
    if data.email in MOCK_USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create new user
    new_user_id = f"user-{str(uuid.uuid4())[:8]}"
    new_user = {
        "email": data.email,
        "password": data.password,  # In real app, this would be hashed
        "name": data.name,
        "id": new_user_id,
        "role": data.role,
        "institution": data.institution,
        "department": data.department,
        "phone": data.phone
    }
    
    # Add to mock users
    MOCK_USERS[data.email] = new_user
    
    # Create tokens for auto-login after registration
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=new_user["email"],
        expires_delta=access_token_expires
    )
    
    from app.core.security import create_refresh_token
    refresh_token = create_refresh_token(subject=new_user["email"])
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": new_user["id"],
            "email": new_user["email"],
            "name": new_user["name"],
            "role": new_user["role"]
        }
    }