import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()

engine = create_async_engine(DATABASE_URL, future=True, echo=False)
async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# PUBLIC_INTERFACE
async def get_db():
    """Yield DB session context for requests."""
    async with async_session_factory() as session:
        yield session
