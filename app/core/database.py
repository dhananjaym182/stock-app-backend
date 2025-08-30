from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Convert PostgreSQL URL to async version
ASYNC_DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=300
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    """Database dependency for FastAPI"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
