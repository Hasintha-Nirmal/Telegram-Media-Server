from sqlalchemy import select, update
from database.models import Media, DownloadQueue, Chat
from .telegram_client import telegram_client
from .config import settings
import os
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MediaDownloader:
    def __init__(self, db_session):
        self.db = db_session
        self.active_downloads = 0
        self.max_parallel = settings.MAX_PARALLEL_DOWNLOADS
    
    async def queue_download(self, media_id):
        """Add media to download queue"""
        # Check if already in queue
        result = await self.db.execute(
            select(DownloadQueue).where(
                DownloadQueue.media_id == media_id,
                DownloadQueue.status.in_(['pending', 'downloading'])
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            return existing.id
        
        # Add to queue
        queue_item = DownloadQueue(media_id=media_id, status='pending')
        self.db.add(queue_item)
        await self.db.commit()
        
        logger.info(f"Added media {media_id} to download queue")
        return queue_item.id
    
    async def process_queue(self):
        """Process download queue"""
        while True:
            try:
                if self.active_downloads >= self.max_parallel:
                    await asyncio.sleep(1)
                    continue
                
                # Get next pending download
                result = await self.db.execute(
                    select(DownloadQueue)
                    .where(DownloadQueue.status == 'pending')
                    .limit(1)
                )
                queue_item = result.scalar_one_or_none()
                
                if not queue_item:
                    await asyncio.sleep(5)
                    continue
                
                # Start download in background
                self.active_downloads += 1
                asyncio.create_task(self._download_media_task(queue_item.id))
                
            except Exception as e:
                logger.error(f"Error in process_queue: {e}")
                await asyncio.sleep(5)
    
    async def _download_media_task(self, queue_id):
        """Download media task wrapper"""
        try:
            await self._download_media(queue_id)
        finally:
            self.active_downloads -= 1
    
    async def _download_media(self, queue_id):
        """Download media from queue"""
        from database.manager import db_manager
        
        # Use a fresh session for this download
        session = await db_manager.get_session()
        
        try:
            try:
                # Get queue item
                result = await session.execute(
                    select(DownloadQueue).where(DownloadQueue.id == queue_id)
                )
                queue_item = result.scalar_one_or_none()
                
                if not queue_item:
                    return
                
                # Update status
                queue_item.status = 'downloading'
                queue_item.started_at = datetime.utcnow()
                await session.commit()
                
                # Get media info
                result = await session.execute(
                    select(Media).where(Media.id == queue_item.media_id)
                )
                media = result.scalar_one_or_none()
                
                if not media:
                    queue_item.status = 'failed'
                    queue_item.error_message = 'Media not found'
                    await session.commit()
                    return
                
                # Get chat info for output path
                result = await session.execute(
                    select(Chat).where(Chat.id == media.chat_id)
                )
                chat = result.scalar_one_or_none()
                
                # Determine output path
                output_path = self._get_output_path_sync(media, chat)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                logger.info(f"Starting download: {media.file_name} to {output_path}")
                
                # Download with progress callback
                def progress_callback(current, total):
                    if total > 0:
                        progress = (current / total) * 100
                        logger.info(f"Download progress for {media.file_name}: {progress:.1f}%")
                
                file_path = await telegram_client.download_media(
                    media.chat_id,
                    media.message_id,
                    output_path,
                    progress_callback
                )
                
                # Update media and queue
                media.downloaded = True
                media.download_path = file_path
                queue_item.status = 'completed'
                queue_item.progress = 100.0
                queue_item.completed_at = datetime.utcnow()
                await session.commit()
                
                logger.info(f"✅ Downloaded media {media.id} ({media.file_name}) to {file_path}")
                
            except Exception as e:
                logger.error(f"Download failed for queue {queue_id}: {e}")
                # Update error in same session
                result = await session.execute(
                    select(DownloadQueue).where(DownloadQueue.id == queue_id)
                )
                queue_item = result.scalar_one_or_none()
                if queue_item:
                    queue_item.status = 'failed'
                    queue_item.error_message = str(e)
                    await session.commit()
        finally:
            await session.close()
    
    def _get_output_path_sync(self, media, chat):
        """Generate output path for media (synchronous version)"""
        # Organize by chat type
        chat_type_folder = {
            'channel': 'channels',
            'supergroup': 'groups',
            'group': 'groups',
            'private': 'users',
            'bot': 'bots'
        }.get(chat.chat_type if chat else 'unknown', 'other')
        
        # Sanitize chat name
        chat_name = "".join(c for c in (chat.name if chat else 'unknown') if c.isalnum() or c in (' ', '-', '_')).strip()
        
        output_dir = os.path.join(
            settings.DOWNLOAD_PATH,
            chat_type_folder,
            chat_name
        )
        
        return os.path.join(output_dir, media.file_name)
    
    async def download_chat_media(self, chat_id, media_type=None):
        """Queue all media from a chat for download"""
        query = select(Media).where(Media.chat_id == chat_id)
        
        if media_type:
            query = query.where(Media.media_type == media_type)
        
        result = await self.db.execute(query)
        media_list = result.scalars().all()
        
        queued = 0
        for media in media_list:
            await self.queue_download(media.id)
            queued += 1
        
        return queued
