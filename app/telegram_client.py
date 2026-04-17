from telethon import TelegramClient
from telethon.tl.types import Channel, Chat, User, MessageMediaPhoto, MessageMediaDocument
from .config import settings
import logging

logger = logging.getLogger(__name__)


class TelegramMediaClient:
    def __init__(self):
        self.client = None
        
    async def connect(self):
        """Connect to Telegram using existing session"""
        try:
            self.client = TelegramClient(
                settings.SESSION_PATH.replace('.session', ''),
                settings.API_ID,
                settings.API_HASH
            )
            await self.client.connect()
            
            if not await self.client.is_user_authorized():
                raise Exception("Session is not authorized. Please create a valid session file.")
            
            me = await self.client.get_me()
            logger.info(f"Connected as {me.first_name} (@{me.username})")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Telegram"""
        if self.client:
            await self.client.disconnect()
    
    async def get_dialogs(self):
        """Get all dialogs (chats)"""
        dialogs = []
        async for dialog in self.client.iter_dialogs():
            chat_data = {
                'id': dialog.id,
                'name': dialog.name,
                'username': getattr(dialog.entity, 'username', None),
                'chat_type': self._get_chat_type(dialog.entity),
                'member_count': getattr(dialog.entity, 'participants_count', None),
                'last_activity': dialog.date
            }
            dialogs.append(chat_data)
        return dialogs
    
    def _get_chat_type(self, entity):
        """Determine chat type"""
        if isinstance(entity, Channel):
            return 'channel' if entity.broadcast else 'supergroup'
        elif isinstance(entity, Chat):
            return 'group'
        elif isinstance(entity, User):
            return 'bot' if entity.bot else 'private'
        return 'unknown'
    
    async def get_media_messages(self, chat_id, limit=None, offset_id=0):
        """Get media messages from a chat"""
        media_messages = []
        
        async for message in self.client.iter_messages(
            chat_id, 
            limit=limit,
            offset_id=offset_id,
            reverse=False
        ):
            if message.media:
                media_data = await self._extract_media_info(message)
                if media_data:
                    media_messages.append(media_data)
        
        return media_messages
    
    async def _extract_media_info(self, message):
        """Extract media information from message"""
        if not message.media:
            return None
        
        media_data = {
            'message_id': message.id,
            'chat_id': message.chat_id,
            'upload_date': message.date,
            'file_name': None,
            'file_size': None,
            'media_type': None,
            'duration': None,
            'width': None,
            'height': None,
            'mime_type': None,
        }
        
        # Photo
        if hasattr(message.media, 'photo') and message.media.photo:
            media_data['media_type'] = 'photo'
            media_data['file_name'] = f"photo_{message.id}.jpg"
            if hasattr(message.media.photo, 'sizes') and message.media.photo.sizes:
                largest = max(message.media.photo.sizes, key=lambda s: getattr(s, 'size', 0) if hasattr(s, 'size') else 0)
                if hasattr(largest, 'size'):
                    media_data['file_size'] = largest.size
                if hasattr(largest, 'w'):
                    media_data['width'] = largest.w
                if hasattr(largest, 'h'):
                    media_data['height'] = largest.h
        
        # Document (video, audio, file, gif)
        elif hasattr(message.media, 'document') and message.media.document:
            doc = message.media.document
            media_data['file_size'] = doc.size
            media_data['mime_type'] = doc.mime_type
            
            # Get file name
            for attr in doc.attributes:
                if hasattr(attr, 'file_name'):
                    media_data['file_name'] = attr.file_name
                if hasattr(attr, 'duration'):
                    media_data['duration'] = attr.duration
                if hasattr(attr, 'w'):
                    media_data['width'] = attr.w
                if hasattr(attr, 'h'):
                    media_data['height'] = attr.h
            
            # Determine media type
            if doc.mime_type:
                if doc.mime_type.startswith('video/'):
                    media_data['media_type'] = 'gif' if 'gif' in doc.mime_type else 'video'
                elif doc.mime_type.startswith('audio/'):
                    media_data['media_type'] = 'audio'
                elif doc.mime_type.startswith('image/'):
                    media_data['media_type'] = 'photo'
                else:
                    media_data['media_type'] = 'document'
            else:
                media_data['media_type'] = 'document'
            
            if not media_data['file_name']:
                ext = doc.mime_type.split('/')[-1] if doc.mime_type else 'bin'
                media_data['file_name'] = f"{media_data['media_type']}_{message.id}.{ext}"
        
        # Voice message
        elif hasattr(message.media, 'voice') or (hasattr(message.media, 'document') and 
                                                   any(hasattr(attr, 'voice') for attr in getattr(message.media.document, 'attributes', []))):
            media_data['media_type'] = 'voice'
            media_data['file_name'] = f"voice_{message.id}.ogg"
        
        return media_data if media_data['media_type'] else None
    
    async def download_media(self, chat_id, message_id, output_path, progress_callback=None):
        """Download media from message"""
        try:
            message = await self.client.get_messages(chat_id, ids=message_id)
            if not message or not message.media:
                return None
            
            file_path = await self.client.download_media(
                message.media,
                file=output_path,
                progress_callback=progress_callback
            )
            return file_path
        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise
    
    async def stream_media(self, chat_id, message_id, offset=0, limit=None):
        """Stream media bytes"""
        try:
            message = await self.client.get_messages(chat_id, ids=message_id)
            if not message or not message.media:
                return  # Just return without value in async generator
            
            # Download in chunks
            async for chunk in self.client.iter_download(message.media, offset=offset, limit=limit):
                yield chunk
        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            raise


# Global client instance
telegram_client = TelegramMediaClient()
