import asyncio
import logging
import uvicorn
from web.api import app
from app.config import settings
from app.telegram_client import telegram_client
from database import async_session
from app.scanner import MediaScanner
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
            
            logger.info("Running auto-sync...")
            async with async_session() as session:
                scanner = MediaScanner(session)
                
                # Scan for new chats
                await scanner.scan_all_chats()
                
                # Scan for new media
                count = await scanner.scan_all_media()
                logger.info(f"Auto-sync completed: {count} new media items")
                
        except Exception as e:
            logger.error(f"Auto-sync failed: {e}")


def main():
    """Main entry point"""
    # Ensure data directories exist
    os.makedirs('/data/session', exist_ok=True)
    os.makedirs('/data/downloads', exist_ok=True)
    os.makedirs('/data/database', exist_ok=True)
    
    # Start auto-sync task in background
    loop = asyncio.get_event_loop()
    loop.create_task(auto_sync_task())
    
    # Start web server
    logger.info(f"Starting server on http://0.0.0.0:8080")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )


if __name__ == "__main__":
    main()
