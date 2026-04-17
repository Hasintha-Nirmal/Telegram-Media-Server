from .telegram_client import telegram_client
import logging

logger = logging.getLogger(__name__)


class MediaStreamer:
    @staticmethod
    async def stream_media(chat_id, message_id, start_byte=0, end_byte=None):
        """Stream media with range support"""
        try:
            chunks = []
            total_size = 0
            
            # Calculate limit if end_byte specified
            limit = (end_byte - start_byte + 1) if end_byte else None
            
            async for chunk in telegram_client.stream_media(
                chat_id, 
                message_id, 
                offset=start_byte,
                limit=limit
            ):
                chunks.append(chunk)
                total_size += len(chunk)
            
            return b''.join(chunks), total_size
            
        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            raise
    
    @staticmethod
    async def get_media_size(chat_id, message_id):
        """Get total media size"""
        try:
            message = await telegram_client.client.get_messages(chat_id, ids=message_id)
            if not message or not message.media:
                return None
            
            if hasattr(message.media, 'document') and message.media.document:
                return message.media.document.size
            elif hasattr(message.media, 'photo') and message.media.photo:
                if hasattr(message.media.photo, 'sizes'):
                    largest = max(message.media.photo.sizes, key=lambda s: getattr(s, 'size', 0) if hasattr(s, 'size') else 0)
                    return getattr(largest, 'size', None)
            
            return None
        except Exception as e:
            logger.error(f"Failed to get media size: {e}")
            return None
