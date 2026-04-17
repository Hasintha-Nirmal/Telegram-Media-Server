from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Boolean, Float, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    username = Column(String, nullable=True)
    chat_type = Column(String, nullable=False)  # channel, group, supergroup, bot, private
    member_count = Column(Integer, nullable=True)
    last_activity = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    media = relationship("Media", back_populates="chat")
    
    __table_args__ = (
        Index('idx_chat_type', 'chat_type'),
        Index('idx_chat_username', 'username'),
    )


class Media(Base):
    __tablename__ = "media"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(BigInteger, nullable=False)
    chat_id = Column(BigInteger, ForeignKey("chats.id"), nullable=False)
    file_name = Column(String, nullable=True)
    file_size = Column(BigInteger, nullable=True)
    media_type = Column(String, nullable=False)  # video, photo, document, audio, voice, gif
    duration = Column(Integer, nullable=True)  # seconds
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    mime_type = Column(String, nullable=True)
    file_reference = Column(String, nullable=True)
    upload_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    downloaded = Column(Boolean, default=False)
    download_path = Column(String, nullable=True)
    
    chat = relationship("Chat", back_populates="media")
    
    __table_args__ = (
        Index('idx_media_type', 'media_type'),
        Index('idx_chat_id', 'chat_id'),
        Index('idx_message_id', 'message_id'),
        Index('idx_file_name', 'file_name'),
        Index('idx_upload_date', 'upload_date'),
    )


class DownloadQueue(Base):
    __tablename__ = "download_queue"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    media_id = Column(Integer, ForeignKey("media.id"), nullable=False)
    status = Column(String, default="pending")  # pending, downloading, completed, failed
    progress = Column(Float, default=0.0)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_status', 'status'),
    )


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(BigInteger, nullable=False)
    chat_id = Column(BigInteger, ForeignKey("chats.id"), nullable=False)
    text = Column(String, nullable=True)
    sender_id = Column(BigInteger, nullable=True)
    sender_name = Column(String, nullable=True)
    date = Column(DateTime, nullable=False)
    reply_to_message_id = Column(BigInteger, nullable=True)
    forward_from = Column(String, nullable=True)
    has_media = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_message_chat_id', 'chat_id'),
        Index('idx_message_date', 'date'),
        Index('idx_message_text', 'text'),
    )


class SyncState(Base):
    __tablename__ = "sync_state"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, unique=True, nullable=False)
    last_message_id = Column(BigInteger, nullable=True)
    last_sync = Column(DateTime, nullable=True)
    total_messages = Column(Integer, default=0)
    total_media = Column(Integer, default=0)
