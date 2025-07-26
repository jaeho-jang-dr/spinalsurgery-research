"""
Initialize database with test data
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import engine, Base, AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash

async def init_db():
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create test user
    async with AsyncSessionLocal() as session: 
        # Check if user exists
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.email == "test@example.com"))
        existing_user = result.scalar_one_or_none()
        
        if not existing_user:
            test_user = User(
                email="test@example.com",
                name="Test User",
                hashed_password=get_password_hash("test1234"),
                role="admin"
            )
            session.add(test_user)
            await session.commit()
            print("Test user created: test@example.com / test1234")
        else:
            print("Test user already exists")

if __name__ == "__main__":
    asyncio.run(init_db())