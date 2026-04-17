from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_session, init_db
from database.models import Chat, Media, DownloadQueue, Message
from app.telegram_client import telegram_client
from app.scanner import MediaScanner
from app.downloader import MediaDownloader
from app.search_engine import SearchEngine
from app.streamer import MediaStreamer
from typing import Optional, List
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

app = FastAPI(title="Telegram Media Server", version="1.0.0")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application"""
    logger.info("Starting Telegram Media Server...")
    
    # Initialize database
    await init_db()
    
    # Connect to Telegram
    await telegram_client.connect()
    
    logger.info("Application started successfully")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await telegram_client.disconnect()


# Root endpoint with new safe UI
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve web interface"""
    with open("web/index.html", "r") as f:
        return f.read()


# API Endpoints

@app.get("/api/chats")
async def get_chats(
    limit: int = Query(1000, ge=1, le=10000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_session)
):
    """Get all chats"""
    result = await db.execute(
        select(Chat).limit(limit).offset(offset)
    )
    chats = result.scalars().all()
    return [
        {
            'id': chat.id,
            'name': chat.name,
            'username': chat.username,
            'chat_type': chat.chat_type,
            'member_count': chat.member_count,
            'last_activity': chat.last_activity.isoformat() if chat.last_activity else None
        }
        for chat in chats
    ]


@app.get("/api/media")
async def get_media(
    chat_id: Optional[int] = None,
    media_type: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_session)
):
    """Get media with filters"""
    query = select(Media).join(Chat)
    
    if chat_id:
        query = query.where(Media.chat_id == chat_id)
    if media_type:
        query = query.where(Media.media_type == media_type)
    
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    media_list = result.scalars().all()
    
    return [
        {
            'id': media.id,
            'message_id': media.message_id,
            'chat_id': media.chat_id,
            'chat_name': media.chat.name,
            'file_name': media.file_name,
            'file_size': media.file_size,
            'media_type': media.media_type,
            'duration': media.duration,
            'upload_date': media.upload_date.isoformat() if media.upload_date else None
        }
        for media in media_list
    ]


@app.get("/api/chat/{chat_id}/messages")
async def get_chat_messages(
    chat_id: int,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_session)
):
    """Get messages from a specific chat"""
    result = await db.execute(
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.date.desc())
        .limit(limit)
        .offset(offset)
    )
    messages = result.scalars().all()
    
    return [
        {
            'id': msg.id,
            'message_id': msg.message_id,
            'text': msg.text,
            'sender_name': msg.sender_name,
            'date': msg.date.isoformat() if msg.date else None,
            'has_media': msg.has_media,
            'reply_to_message_id': msg.reply_to_message_id,
            'forward_from': msg.forward_from
        }
        for msg in messages
    ]


@app.post("/api/scan/chats")
async def scan_chats(db: AsyncSession = Depends(get_session)):
    """Scan all chats"""
    scanner = MediaScanner(db)
    count = await scanner.scan_all_chats()
    return {'count': count}


@app.post("/api/scan/chat/{chat_id}")
async def scan_chat_media(chat_id: int, db: AsyncSession = Depends(get_session)):
    """Scan media from specific chat"""
    scanner = MediaScanner(db)
    count = await scanner.scan_chat_media(chat_id)
    return {'count': count}


@app.post("/api/scan/chat/{chat_id}/messages")
async def scan_chat_messages(
    chat_id: int,
    limit: Optional[int] = Query(1000, description="Max messages to scan (default: 1000)"),
    db: AsyncSession = Depends(get_session)
):
    """Scan text messages from specific chat"""
    scanner = MediaScanner(db)
    count = await scanner.scan_chat_messages(chat_id, limit=limit)
    return {'count': count}


@app.post("/api/download/{media_id}")
async def download_media(media_id: int, db: AsyncSession = Depends(get_session)):
    """Queue media for download"""
    downloader = MediaDownloader(db)
    queue_id = await downloader.queue_download(media_id)
    return {'queue_id': queue_id, 'status': 'queued'}


@app.get("/stream/{media_id}")
async def stream_media(media_id: int, request: Request, db: AsyncSession = Depends(get_session)):
    """Stream media with range support"""
    # Get media info
    result = await db.execute(
        select(Media).where(Media.id == media_id)
    )
    media = result.scalar_one_or_none()
    
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Get file size
    file_size = await MediaStreamer.get_media_size(media.chat_id, media.message_id)
    
    if not file_size:
        raise HTTPException(status_code=404, detail="Media size unavailable")
    
    # Parse range header
    range_header = request.headers.get('range')
    start = 0
    end = file_size - 1
    
    if range_header:
        range_match = range_header.replace('bytes=', '').split('-')
        start = int(range_match[0]) if range_match[0] else 0
        end = int(range_match[1]) if len(range_match) > 1 and range_match[1] else end
    
    # Stream media
    async def stream_generator():
        async for chunk in telegram_client.stream_media(media.chat_id, media.message_id, offset=start, limit=end-start+1):
            yield chunk
    
    headers = {
        'Content-Range': f'bytes {start}-{end}/{file_size}',
        'Accept-Ranges': 'bytes',
        'Content-Length': str(end - start + 1),
        'Content-Type': media.mime_type or 'application/octet-stream'
    }
    
    status_code = 206 if range_header else 200
    
    return StreamingResponse(stream_generator(), status_code=status_code, headers=headers)
