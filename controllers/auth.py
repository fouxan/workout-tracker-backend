from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.auth import User
from services.auth import hash_password
from schemas.auth import *


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_data: SignupRequest):
    hashed_password = hash_password(user_data.password)
    print("Creating user with pw:", hashed_password)
    user = User(
        email=user_data.email,
        password=hashed_password,
        username=user_data.username,
        plan=user_data.plan,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    print("User created:", user)
    return user
