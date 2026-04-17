#!/usr/bin/env python3
"""
Script to migrate from SQLite to PostgreSQL
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from database.models import Base
import os

async def migrate():
    # PostgreSQL connection
    postgres_url = os.getenv("POSTGRES_URL", "postgresql+asyncpg://user:pass@localhost/telegram_media")
    
    print(f"Creating tables in PostgreSQL: {postgres_url}")
    
    engine = create_async_engine(postgres_url, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Migration completed!")
    print("\nUpdate your .env file:")
    print(f"DATABASE_URL={postgres_url}")

if __name__ == "__main__":
    asyncio.run(migrate())
