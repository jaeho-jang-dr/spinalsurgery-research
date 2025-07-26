"""
Mock authentication for testing without database
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token
from app.core.config import settings

router = APIRouter()

# Mock users
MOCK_USERS = {
    "test@example.com": {
        "email": "test@example.com",
        "password": "test1234",
        "name": "Test User",
        "id": "test-user-id",
        "role": "admin"
    }
}

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