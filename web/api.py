from fastapi import FastAPI, Depends, HTTPException, Query, Request, UploadFile, File
from fastapi.responses import StreamingResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_session, init_db
from database.models import Chat, Media, DownloadQueue, Message
from database.manager import db_manager
from app.telegram_client import telegram_client
from app.scanner import MediaScanner
from app.downloader import MediaDownloader
from app.search_engine import SearchEngine
from app.streamer import MediaStreamer
from app.config import settings
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
import logging
import os
import asyncio
import shutil

logger = logging.getLogger(__name__)

app = FastAPI(title="Telegram Media Server", version="1.0.0")

# Background task references
background_tasks = []


# Pydantic models for requests
class SessionCreateRequest(BaseModel):
    session_name: str
    phone: str

class SessionVerifyRequest(BaseModel):
    session_name: str
    phone: str
    code: str

class SessionPasswordRequest(BaseModel):
    session_name: str
    password: str

class SessionSwitchRequest(BaseModel):
    session_name: str


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application"""
    logger.info("Starting Telegram Media Server...")
    
    # Initialize database
    await init_db()
    
    # Connect to Telegram
    await telegram_client.connect()
    
    # Start background workers
    from main import auto_sync_task, download_queue_worker
    
    logger.info("Starting background workers...")
    background_tasks.append(asyncio.create_task(auto_sync_task()))
    background_tasks.append(asyncio.create_task(download_queue_worker()))
    logger.info("Background workers started")
    
    logger.info("Application started successfully")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down background workers...")
    for task in background_tasks:
        task.cancel()
    await telegram_client.disconnect()
    logger.info("Shutdown complete")


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
    
    logger.info(f"Returning {len(chats)} chats for account: {db_manager.current_account}")
    
    # Log first few chats for debugging
    if chats:
        for i, chat in enumerate(chats[:3]):
            logger.info(f"Chat {i}: id={chat.id}, name={chat.name}, type={chat.chat_type}")
    
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


# Session Management Endpoints

@app.get("/api/sessions")
async def list_sessions():
    """List all available session files"""
    sessions = telegram_client.list_sessions()
    current_user = await telegram_client.get_current_user()
    return {
        'sessions': sessions,
        'current_user': current_user
    }


@app.post("/api/sessions/create")
async def create_session(request: SessionCreateRequest):
    """Start session creation process"""
    try:
        result = await telegram_client.create_session(request.session_name, request.phone)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/sessions/verify")
async def verify_session(request: SessionVerifyRequest):
    """Verify code and complete session creation"""
    try:
        result = await telegram_client.verify_code(
            request.session_name,
            request.phone,
            request.code
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/sessions/password")
async def verify_password(request: SessionPasswordRequest):
    """Verify 2FA password after code verification"""
    try:
        result = await telegram_client.verify_password(
            request.session_name,
            request.password
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/sessions/switch")
async def switch_session(request: dict):
    """Switch to a different session"""
    try:
        session_name = request.get('session_name')
        if not session_name:
            raise HTTPException(status_code=400, detail="session_name is required")
        
        logger.info(f"Switching to session: {session_name}")
        user = await telegram_client.connect(session_name)
        return {
            'status': 'success',
            'user': {
                'id': user.id,
                'first_name': user.first_name,
                'username': user.username,
                'phone': user.phone
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to switch session: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/sessions/upload")
async def upload_session(file: UploadFile = File(...)):
    """Upload a session file"""
    try:
        if not file.filename.endswith('.session'):
            raise HTTPException(status_code=400, detail="File must be a .session file")
        
        file_path = os.path.join(settings.SESSION_DIR, file.filename)
        
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)
        
        return {
            'status': 'success',
            'filename': file.filename,
            'message': 'Session file uploaded successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/sessions/{session_name}")
async def delete_session(session_name: str):
    """Delete a session file"""
    try:
        file_path = os.path.join(settings.SESSION_DIR, session_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            return {'status': 'success', 'message': f'Session {session_name} deleted'}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/media")
async def get_media(
    chat_id: Optional[int] = None,
    media_type: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_session)
):
    """Get media with filters"""
    from sqlalchemy.orm import selectinload
    
    query = select(Media).options(selectinload(Media.chat))
    
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
            'chat_name': media.chat.name if media.chat else 'Unknown',
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
async def scan_chat_media(
    chat_id: int,
    full: bool = Query(False, description="Force full scan instead of incremental"),
    db: AsyncSession = Depends(get_session)
):
    """Scan media from specific chat"""
    try:
        scanner = MediaScanner(db)
        count = await scanner.scan_chat_media(chat_id, incremental=not full, force_full=full)
        return {'count': count}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error scanning chat {chat_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to scan chat: {str(e)}")


@app.post("/api/scan/chat/{chat_id}/messages")
async def scan_chat_messages(
    chat_id: int,
    limit: Optional[int] = Query(1000, description="Max messages to scan (default: 1000)"),
    db: AsyncSession = Depends(get_session)
):
    """Scan text messages from specific chat"""
    try:
        scanner = MediaScanner(db)
        count = await scanner.scan_chat_messages(chat_id, limit=limit)
        return {'count': count}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error scanning messages from chat {chat_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to scan messages: {str(e)}")


@app.post("/api/download/{media_id}")
async def download_media(media_id: int, db: AsyncSession = Depends(get_session)):
    """Queue media for download"""
    downloader = MediaDownloader(db)
    queue_id = await downloader.queue_download(media_id)
    return {'queue_id': queue_id, 'status': 'queued'}


@app.get("/api/queue")
async def get_download_queue(db: AsyncSession = Depends(get_session)):
    """Get download queue status"""
    result = await db.execute(
        select(DownloadQueue).order_by(DownloadQueue.created_at.desc()).limit(50)
    )
    queue_items = result.scalars().all()
    
    return [
        {
            'id': item.id,
            'media_id': item.media_id,
            'status': item.status,
            'progress': item.progress,
            'error_message': item.error_message,
            'created_at': item.created_at.isoformat() if item.created_at else None,
            'started_at': item.started_at.isoformat() if item.started_at else None,
            'completed_at': item.completed_at.isoformat() if item.completed_at else None
        }
        for item in queue_items
    ]


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
