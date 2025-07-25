from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserSchema)
async def read_user_me(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get current user"""
    return current_user


@router.put("/me", response_model=UserSchema)
async def update_user_me(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Update current user"""
    if user_in.email and user_in.email != current_user.email:
        # Check if email already exists
        result = await db.execute(
            select(User).where(User.email == user_in.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
    
    update_data = user_in.dict(exclude_unset=True)
    
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["password_hash"] = hashed_password
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.post("/change-password")
async def change_password(
    *,
    db: AsyncSession = Depends(get_db),
    current_password: str,
    new_password: str,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Change user password"""
    if not verify_password(current_password, current_user.password_hash):
        raise HTTPException(
            status_code=400,
            detail="Incorrect password"
        )
    
    current_user.password_hash = get_password_hash(new_password)
    db.add(current_user)
    await db.commit()
    
    return {"message": "Password updated successfully"}