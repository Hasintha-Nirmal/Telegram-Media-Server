"""
Database manager for per-account database isolation
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .models import Base
import os
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages separate databases for each account"""
    
    def __init__(self):
        self.engines = {}
        self.session_makers = {}
        self.current_account = None
    
    def get_db_path(self, account_name: str) -> str:
        """Get database path for specific account"""
        # Remove .session extension if present
        if account_name.endswith('.session'):
            account_name = account_name[:-8]
        
        # Sanitize account name for filename
        safe_name = "".join(c for c in account_name if c.isalnum() or c in ('-', '_'))
        return f"sqlite+aiosqlite:////data/database/{safe_name}.db"
    
    async def get_engine(self, account_name: str):
        """Get or create engine for account"""
        if account_name not in self.engines:
            db_url = self.get_db_path(account_name)
            logger.info(f"Creating database engine for account: {account_name} at {db_url}")
            
            engine = create_async_engine(
                db_url,
                echo=False,
                connect_args={"check_same_thread": False}
            )
            
            # Initialize tables
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            self.engines[account_name] = engine
            self.session_makers[account_name] = sessionmaker(
                engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
        
        return self.engines[account_name]
    
    async def get_session(self, account_name: str = None):
        """Get database session for account"""
        if account_name is None:
            account_name = self.current_account
        
        if account_name is None:
            raise ValueError("No account specified and no current account set")
        
        await self.get_engine(account_name)
        return self.session_makers[account_name]()
    
    def set_current_account(self, account_name: str):
        """Set the current active account"""
        logger.info(f"Setting current account to: {account_name}")
        self.current_account = account_name
    
    async def close_all(self):
        """Close all database connections"""
        for account_name, engine in self.engines.items():
            logger.info(f"Closing database for account: {account_name}")
            await engine.dispose()
        
        self.engines.clear()
        self.session_makers.clear()


# Global database manager instance
db_manager = DatabaseManager()
