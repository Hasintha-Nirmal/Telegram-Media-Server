import asyncio
import logging
import uvicorn
from app.config import settings
from database import async_session
from app.scanner import MediaScanner
from app.downloader import MediaDownloader
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def auto_sync_task():
    """Background task for auto-syncing media"""
    logger.info("Starting auto-sync task...")
    
    while True:
        try:
            await asyncio.sleep(settings.SYNC_INTERVAL)
            
            # Only sync if there's an active account
            from database.manager import db_manager
            if not db_manager.current_account:
                logger.debug("No active account, skipping auto-sync")
                continue
            
            logger.info(f"Running auto-sync for account: {db_manager.current_account}")
            session = await db_manager.get_session()
            
            try:
                scanner = MediaScanner(session)
                
                # Scan for new chats
                await scanner.scan_all_chats()
                
                # Scan for new media
                count = await scanner.scan_all_media()
                logger.info(f"Auto-sync completed: {count} new media items")
            finally:
                await session.close()
                
        except Exception as e:
            logger.error(f"Auto-sync failed: {e}")


async def download_queue_worker():
    """Background task for processing download queue"""
    logger.info("Starting download queue worker...")
    
    while True:
        try:
            # Only process if there's an active account
            from database.manager import db_manager
            if not db_manager.current_account:
                await asyncio.sleep(5)
                continue
            
            session = await db_manager.get_session()
            
            try:
                downloader = MediaDownloader(session)
                await downloader.process_queue()
            finally:
                await session.close()
                
        except Exception as e:
            logger.error(f"Download queue worker error: {e}")
            await asyncio.sleep(5)


def main():
    """Main entry point"""
    # Ensure data directories exist
    os.makedirs('/data/session', exist_ok=True)
    os.makedirs('/data/downloads', exist_ok=True)
    os.makedirs('/data/database', exist_ok=True)
    
    # Start web server
    logger.info(f"Starting server on http://0.0.0.0:8080")
    uvicorn.run(
        "web.api:app",
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )


if __name__ == "__main__":
    main()
