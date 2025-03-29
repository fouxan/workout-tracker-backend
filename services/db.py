# dependencies.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db():
    async with async_session() as session:
        yield session