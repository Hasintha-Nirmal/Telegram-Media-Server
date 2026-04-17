from sqlalchemy import select
from database.models import Chat, Media, SyncState, Message
from .telegram_client import telegram_client
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MediaScanner:
    def __init__(self, db_session):
        self.db = db_session
    
    async def scan_all_chats(self):
        """Discover and index all chats"""
        logger.info("Starting chat discovery...")
        dialogs = await telegram_client.get_dialogs()
        
        for dialog_data in dialogs:
            await self._save_chat(dialog_data)
        
        logger.info(f"Discovered {len(dialogs)} chats")
        return len(dialogs)
    
    async def _save_chat(self, chat_data):
        """Save or update chat in database"""
        result = await self.db.execute(
            select(Chat).where(Chat.id == chat_data['id'])
        )
        chat = result.scalar_one_or_none()
        
        if chat:
            # Update existing
            chat.name = chat_data['name']
            chat.username = chat_data['username']
            chat.chat_type = chat_data['chat_type']
            chat.member_count = chat_data['member_count']
            chat.last_activity = chat_data['last_activity']
            chat.updated_at = datetime.utcnow()
        else:
            # Create new
            chat = Chat(**chat_data)
            self.db.add(chat)
        
        await self.db.commit()
        return chat
    
    async def scan_chat_media(self, chat_id, incremental=True):
        """Scan media from a specific chat"""
        logger.info(f"Scanning media from chat {chat_id}...")
        
        # Get sync state
        offset_id = 0
        if incremental:
            result = await self.db.execute(
                select(SyncState).where(SyncState.chat_id == chat_id)
            )
            sync_state = result.scalar_one_or_none()
            if sync_state and sync_state.last_message_id:
                offset_id = sync_state.last_message_id
        
        # Fetch media messages
        media_messages = await telegram_client.get_media_messages(
            chat_id, 
            offset_id=offset_id
        )
        
        # Save media to database
        saved_count = 0
        last_message_id = offset_id
        
        for media_data in media_messages:
            await self._save_media(media_data)
            saved_count += 1
            last_message_id = max(last_message_id, media_data['message_id'])
        
        # Update sync state
        await self._update_sync_state(chat_id, last_message_id, saved_count)
        
        logger.info(f"Indexed {saved_count} media items from chat {chat_id}")
        return saved_count
    
    async def scan_chat_messages(self, chat_id, limit=None, incremental=True):
        """Scan text messages from a specific chat"""
        logger.info(f"Scanning messages from chat {chat_id}...")
        
        try:
            # Get sync state
            offset_id = 0
            if incremental:
                result = await self.db.execute(
                    select(SyncState).where(SyncState.chat_id == chat_id)
                )
                sync_state = result.scalar_one_or_none()
                if sync_state and sync_state.last_message_id:
                    offset_id = sync_state.last_message_id
            
            # Fetch all messages
            logger.info(f"Fetching messages from chat {chat_id}, offset_id={offset_id}, limit={limit}")
            messages = await telegram_client.get_messages(
                chat_id,
                limit=limit,
                offset_id=offset_id
            )
            
            logger.info(f"Fetched {len(messages)} messages from chat {chat_id}")
            
            # Save messages to database
            saved_count = 0
            last_message_id = offset_id
            
            for msg_data in messages:
                try:
                    await self._save_message(msg_data)
                    saved_count += 1
                    last_message_id = max(last_message_id, msg_data['message_id'])
                    
                    # Log progress every 100 messages
                    if saved_count % 100 == 0:
                        logger.info(f"Saved {saved_count} messages so far...")
                except Exception as e:
                    logger.error(f"Error saving message {msg_data['message_id']}: {e}")
                    continue
            
            # Update sync state
            await self._update_sync_state(chat_id, last_message_id, 0, saved_count)
            
            logger.info(f"Indexed {saved_count} messages from chat {chat_id}")
            return saved_count
            
        except Exception as e:
            logger.error(f"Error scanning messages from chat {chat_id}: {e}")
            raise
    
    async def _save_media(self, media_data):
        """Save media to database"""
        # Check if already exists
        result = await self.db.execute(
            select(Media).where(
                Media.chat_id == media_data['chat_id'],
                Media.message_id == media_data['message_id']
            )
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            media = Media(**media_data)
            self.db.add(media)
            await self.db.commit()
    
    async def _save_message(self, message_data):
        """Save message to database"""
        # Check if already exists
        result = await self.db.execute(
            select(Message).where(
                Message.chat_id == message_data['chat_id'],
                Message.message_id == message_data['message_id']
            )
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            message = Message(**message_data)
            self.db.add(message)
            await self.db.commit()
    
    async def _update_sync_state(self, chat_id, last_message_id, media_count, message_count=0):
        """Update sync state for chat"""
        result = await self.db.execute(
            select(SyncState).where(SyncState.chat_id == chat_id)
        )
        sync_state = result.scalar_one_or_none()
        
        if sync_state:
            sync_state.last_message_id = last_message_id
            sync_state.last_sync = datetime.utcnow()
            sync_state.total_media += media_count
            sync_state.total_messages += message_count
        else:
            sync_state = SyncState(
                chat_id=chat_id,
                last_message_id=last_message_id,
                last_sync=datetime.utcnow(),
                total_media=media_count,
                total_messages=message_count
            )
            self.db.add(sync_state)
        
        await self.db.commit()
    
    async def scan_all_media(self):
        """Scan media from all chats"""
        result = await self.db.execute(select(Chat))
        chats = result.scalars().all()
        
        total_media = 0
        for chat in chats:
            try:
                count = await self.scan_chat_media(chat.id)
                total_media += count
            except Exception as e:
                logger.error(f"Failed to scan chat {chat.id}: {e}")
        
        return total_media
