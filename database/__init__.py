from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .models import Base, Chat, Media, DownloadQueue, SyncState, Message
from .manager import db_manager
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:////data/database/media.db")

# Legacy single database support (for backward compatibility)
engine = create_async_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Get database session for current account"""
    if db_manager.current_account:
        # Use per-account database
        session = await db_manager.get_session()
        try:
            yield session
        finally:
            await session.close()
    else:
        # Fallback to legacy single database
        async with async_session() as session:
            yield session
