from telethon import TelegramClient
from telethon.tl.types import Channel, Chat, User, MessageMediaPhoto, MessageMediaDocument
from .config import settings
import logging
import os

logger = logging.getLogger(__name__)


class TelegramMediaClient:
    def __init__(self):
        self.client = None
        self.current_session = None
        self.pending_clients = {}  # Store pending session clients
        
    async def connect(self, session_name: str = None):
        """Connect to Telegram using specified session"""
        try:
            # Disconnect existing client if any
            if self.client:
                await self.client.disconnect()
            
            # Determine session path
            if session_name:
                session_path = os.path.join(settings.SESSION_DIR, session_name)
            else:
                session_path = settings.SESSION_PATH
            
            # Remove .session extension if present
            if session_path.endswith('.session'):
                session_path = session_path[:-8]
            
            self.current_session = os.path.basename(session_path)
            
            self.client = TelegramClient(
                session_path,
                settings.API_ID,
                settings.API_HASH
            )
            await self.client.connect()
            
            if not await self.client.is_user_authorized():
                raise Exception("Session is not authorized. Please create a valid session file.")
            
            me = await self.client.get_me()
            logger.info(f"Connected as {me.first_name} (@{me.username}) using session: {self.current_session}")
            return me
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            raise
    
    async def create_session(self, session_name: str, phone: str):
        """Create a new session interactively"""
        try:
            session_path = os.path.join(settings.SESSION_DIR, session_name)
            if session_path.endswith('.session'):
                session_path = session_path[:-8]
            
            # Clean up any existing pending client for this session
            if session_name in self.pending_clients:
                try:
                    await self.pending_clients[session_name].disconnect()
                except:
                    pass
                del self.pending_clients[session_name]
            
            client = TelegramClient(
                session_path,
                settings.API_ID,
                settings.API_HASH
            )
            
            await client.connect()
            
            # Send code request
            await client.send_code_request(phone)
            
            # Store client for verification step
            self.pending_clients[session_name] = client
            
            logger.info(f"Code sent to {phone} for session {session_name}")
            
            return {
                'session_name': session_name,
                'phone': phone,
                'status': 'code_sent'
            }
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise
    
    async def verify_code(self, session_name: str, phone: str, code: str, password: str = None):
        """Verify code and complete session creation"""
        session_path = os.path.join(settings.SESSION_DIR, session_name)
        if session_path.endswith('.session'):
            session_path = session_path[:-8]
        
        # Try to reuse pending client first
        client = self.pending_clients.get(session_name)
        
        if not client:
            # If no pending client, create new one (user might have refreshed page)
            logger.warning(f"No pending client for {session_name}, creating new connection")
            client = TelegramClient(
                session_path,
                settings.API_ID,
                settings.API_HASH
            )
            await client.connect()
        
        try:
            # Sign in with code
            await client.sign_in(phone, code)
            
            # Success! Get user info
            me = await client.get_me()
            await client.disconnect()
            
            # Clean up pending client
            if session_name in self.pending_clients:
                del self.pending_clients[session_name]
            
            logger.info(f"Successfully created session for {me.first_name} (@{me.username})")
            
            return {
                'session_name': session_name,
                'user': {
                    'id': me.id,
                    'first_name': me.first_name,
                    'username': me.username,
                    'phone': me.phone
                },
                'status': 'success',
                'requires_2fa': False
            }
            
        except Exception as sign_in_error:
            error_msg = str(sign_in_error)
            logger.error(f"Sign in error: {error_msg}")
            
            # Check if 2FA is required
            if 'SessionPasswordNeededError' in str(type(sign_in_error)) or \
               'password' in error_msg.lower() or \
               'two-step' in error_msg.lower() or \
               'two-factor' in error_msg.lower():
                
                # 2FA is required - keep client alive and ask for password
                logger.info(f"2FA required for {session_name}")
                return {
                    'session_name': session_name,
                    'status': 'requires_2fa',
                    'requires_2fa': True,
                    'message': 'Two-factor authentication is enabled. Please enter your password.'
                }
            
            # Other errors - clean up and report
            try:
                await client.disconnect()
                if session_name in self.pending_clients:
                    del self.pending_clients[session_name]
                    
                session_file = session_path + '.session'
                if os.path.exists(session_file):
                    os.remove(session_file)
                    logger.info(f"Cleaned up failed session file: {session_file}")
            except:
                pass
            
            # Provide user-friendly error messages
            if 'expired' in error_msg.lower():
                raise Exception("Verification code expired. Please start over and request a new code.")
            elif 'invalid' in error_msg.lower() or 'phone_code_invalid' in error_msg.lower():
                raise Exception("Invalid verification code. Please check the code and try again, or start over if it expired.")
            elif 'phone_code_hash' in error_msg.lower() or 'key is not registered' in error_msg.lower():
                raise Exception("Session expired. Please close this dialog and start over by clicking 'Add Account' again.")
            elif 'flood' in error_msg.lower():
                raise Exception("Too many attempts. Please wait a few minutes and try again.")
            else:
                raise Exception(f"Sign in failed: {error_msg}")
    
    async def verify_password(self, session_name: str, password: str):
        """Verify 2FA password after code verification"""
        session_path = os.path.join(settings.SESSION_DIR, session_name)
        if session_path.endswith('.session'):
            session_path = session_path[:-8]
        
        # Get pending client
        client = self.pending_clients.get(session_name)
        
        if not client:
            raise Exception("Session expired. Please start over by clicking 'Add Account' again.")
        
        try:
            # Sign in with password
            await client.sign_in(password=password)
            
            # Success! Get user info
            me = await client.get_me()
            await client.disconnect()
            
            # Clean up pending client
            if session_name in self.pending_clients:
                del self.pending_clients[session_name]
            
            logger.info(f"Successfully created session with 2FA for {me.first_name} (@{me.username})")
            
            return {
                'session_name': session_name,
                'user': {
                    'id': me.id,
                    'first_name': me.first_name,
                    'username': me.username,
                    'phone': me.phone
                },
                'status': 'success'
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"2FA password error: {error_msg}")
            
            # Clean up on failure
            try:
                await client.disconnect()
                if session_name in self.pending_clients:
                    del self.pending_clients[session_name]
                    
                session_file = session_path + '.session'
                if os.path.exists(session_file):
                    os.remove(session_file)
            except:
                pass
            
            # Provide user-friendly error
            if 'password' in error_msg.lower() and 'invalid' in error_msg.lower():
                raise Exception("Incorrect 2FA password. Please try again or start over.")
            else:
                raise Exception(f"2FA verification failed: {error_msg}")
    
    def list_sessions(self):
        """List all available session files"""
        try:
            sessions = []
            if os.path.exists(settings.SESSION_DIR):
                for file in os.listdir(settings.SESSION_DIR):
                    if file.endswith('.session'):
                        sessions.append(file)
            return sessions
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return []
    
    async def get_current_user(self):
        """Get current logged in user info"""
        if self.client and await self.client.is_user_authorized():
            me = await self.client.get_me()
            return {
                'id': me.id,
                'first_name': me.first_name,
                'last_name': me.last_name,
                'username': me.username,
                'phone': me.phone,
                'session': self.current_session
            }
        return None
    
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
    
    async def get_messages(self, chat_id, limit=None, offset_id=0):
        """Get all messages (text and media) from a chat"""
        messages = []
        
        async for message in self.client.iter_messages(
            chat_id,
            limit=limit,
            offset_id=offset_id,
            reverse=False
        ):
            message_data = {
                'message_id': message.id,
                'chat_id': message.chat_id,
                'text': message.text or '',
                'sender_id': message.sender_id,
                'sender_name': None,
                'date': message.date,
                'reply_to_message_id': message.reply_to_msg_id if hasattr(message, 'reply_to_msg_id') else None,
                'forward_from': None,
                'has_media': bool(message.media)
            }
            
            # Get sender name
            if message.sender:
                if hasattr(message.sender, 'first_name'):
                    message_data['sender_name'] = message.sender.first_name
                    if hasattr(message.sender, 'last_name') and message.sender.last_name:
                        message_data['sender_name'] += f" {message.sender.last_name}"
                elif hasattr(message.sender, 'title'):
                    message_data['sender_name'] = message.sender.title
            
            # Get forward info
            if message.forward:
                if hasattr(message.forward, 'from_name'):
                    message_data['forward_from'] = message.forward.from_name
                elif hasattr(message.forward, 'from_id'):
                    message_data['forward_from'] = str(message.forward.from_id)
            
            messages.append(message_data)
        
        return messages
    
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
                    # Check if it's a video file by extension
                    if media_data.get('file_name'):
                        ext = media_data['file_name'].lower().split('.')[-1]
                        if ext in ['mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'webm', 'm4v', '3gp']:
                            media_data['media_type'] = 'video'
                        else:
                            media_data['media_type'] = 'document'
                    else:
                        media_data['media_type'] = 'document'
            else:
                # No mime type, check by extension
                if media_data.get('file_name'):
                    ext = media_data['file_name'].lower().split('.')[-1]
                    if ext in ['mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'webm', 'm4v', '3gp']:
                        media_data['media_type'] = 'video'
                    elif ext in ['mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a']:
                        media_data['media_type'] = 'audio'
                    elif ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']:
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
