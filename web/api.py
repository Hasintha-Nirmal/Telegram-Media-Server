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


# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve web interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Telegram Media Server</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
            h1 { color: #0088cc; }
            .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
            .button { background: #0088cc; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
            .button:hover { background: #006699; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
            .stat-card { background: #f5f5f5; padding: 15px; border-radius: 8px; }
            .stat-value { font-size: 24px; font-weight: bold; color: #0088cc; }
        </style>
    </head>
    <body>
        <h1>📱 Telegram Media Server</h1>
        
        <div class="section">
            <h2>Dashboard</h2>
            <div class="stats" id="stats">
                <div class="stat-card">
                    <div>Total Chats</div>
                    <div class="stat-value" id="total-chats">-</div>
                </div>
                <div class="stat-card">
                    <div>Total Media</div>
                    <div class="stat-value" id="total-media">-</div>
                </div>
                <div class="stat-card">
                    <div>Total Storage</div>
                    <div class="stat-value" id="total-storage">-</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Actions</h2>
            <button class="button" onclick="scanChats()">🔍 Scan Chats</button>
            <button class="button" onclick="scanMedia()">📥 Scan All Media</button>
            <button class="button" onclick="viewChats()">💬 View Chats</button>
            <button class="button" onclick="viewMedia()">🎬 View Media</button>
            <button class="button" onclick="viewMessages()">💭 View Messages</button>
        </div>
        
        <div class="section">
            <h2>Search Media</h2>
            <input type="text" id="search-query" placeholder="Search by filename or chat..." style="width: 300px; padding: 8px;">
            <select id="media-type" style="padding: 8px;">
                <option value="">All Types</option>
                <option value="video">Videos</option>
                <option value="photo">Photos</option>
                <option value="audio">Audio</option>
                <option value="document">Documents</option>
            </select>
            <button class="button" onclick="searchMedia()">Search</button>
        </div>
        
        <div class="section" id="results">
            <h2>Results</h2>
            <div id="results-content">Select an action to view results</div>
        </div>
        
        <script>
            async function loadStats() {
                const response = await fetch('/api/stats');
                const data = await response.json();
                document.getElementById('total-chats').textContent = data.total_chats;
                document.getElementById('total-media').textContent = data.total_media;
                document.getElementById('total-storage').textContent = formatBytes(data.total_storage);
            }
            
            async function scanChats() {
                document.getElementById('results-content').innerHTML = 'Scanning chats...';
                const response = await fetch('/api/scan/chats', { method: 'POST' });
                const data = await response.json();
                document.getElementById('results-content').innerHTML = `✅ Scanned ${data.count} chats`;
                loadStats();
            }
            
            async function scanMedia() {
                document.getElementById('results-content').innerHTML = 'Scanning media (this may take a while)...';
                const response = await fetch('/api/scan/media', { method: 'POST' });
                const data = await response.json();
                document.getElementById('results-content').innerHTML = `✅ Indexed ${data.count} media items`;
                loadStats();
            }
            
            async function viewChats() {
                const response = await fetch('/api/chats');
                const chats = await response.json();
                let html = '<table style="width:100%; border-collapse: collapse;"><tr><th>Name</th><th>Type</th><th>Username</th><th>Actions</th></tr>';
                chats.forEach(chat => {
                    html += `<tr style="border-bottom: 1px solid #ddd;">
                        <td style="padding: 10px;">${chat.name}</td>
                        <td>${chat.chat_type}</td>
                        <td>${chat.username || '-'}</td>
                        <td>
                            <button class="button" onclick="viewChatMedia(${chat.id})">View Media</button>
                            <button class="button" onclick="viewChatMessages(${chat.id})">View Messages</button>
                            <button class="button" onclick="scanChatMessages(${chat.id})">Scan Messages</button>
                        </td>
                    </tr>`;
                });
                html += '</table>';
                document.getElementById('results-content').innerHTML = html;
            }
            
            async function viewMedia() {
                const response = await fetch('/api/media?limit=50');
                const media = await response.json();
                displayMedia(media);
            }
            
            async function viewChatMedia(chatId) {
                const response = await fetch(`/api/media?chat_id=${chatId}&limit=50`);
                const media = await response.json();
                displayMedia(media);
            }
            
            async function viewMessages() {
                const response = await fetch('/api/messages?limit=50');
                const messages = await response.json();
                displayMessages(messages);
            }
            
            async function viewChatMessages(chatId) {
                const response = await fetch(`/api/chat/${chatId}/messages?limit=100`);
                const messages = await response.json();
                displayMessages(messages);
            }
            
            async function scanChatMessages(chatId) {
                document.getElementById('results-content').innerHTML = 'Scanning messages...';
                const response = await fetch(`/api/scan/chat/${chatId}/messages`, { method: 'POST' });
                const data = await response.json();
                document.getElementById('results-content').innerHTML = `✅ Scanned ${data.count} messages`;
                loadStats();
            }
            
            function displayMessages(messages) {
                if (messages.length === 0) {
                    document.getElementById('results-content').innerHTML = 'No messages found';
                    return;
                }
                let html = '<div style="max-width: 800px;">';
                messages.forEach(msg => {
                    const date = new Date(msg.date).toLocaleString();
                    const mediaIcon = msg.has_media ? '📎' : '';
                    html += `<div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px; background: #f9f9f9;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                            <strong>${msg.sender_name || 'Unknown'}</strong>
                            <span style="color: #666; font-size: 12px;">${date} ${mediaIcon}</span>
                        </div>
                        <div style="white-space: pre-wrap;">${msg.text || '(No text)'}</div>
                        ${msg.reply_to_message_id ? `<div style="margin-top: 5px; color: #666; font-size: 12px;">↩️ Reply to message ${msg.reply_to_message_id}</div>` : ''}
                        ${msg.forward_from ? `<div style="margin-top: 5px; color: #666; font-size: 12px;">↪️ Forwarded from ${msg.forward_from}</div>` : ''}
                    </div>`;
                });
                html += '</div>';
                document.getElementById('results-content').innerHTML = html;
            }
            
            async function searchMedia() {
                const query = document.getElementById('search-query').value;
                const type = document.getElementById('media-type').value;
                const response = await fetch(`/api/search?q=${query}&media_type=${type}&limit=50`);
                const media = await response.json();
                displayMedia(media);
            }
            
            function displayMedia(media) {
                if (media.length === 0) {
                    document.getElementById('results-content').innerHTML = 'No media found';
                    return;
                }
                let html = '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px;">';
                media.forEach(item => {
                    const icon = {'video': '🎬', 'photo': '🖼️', 'audio': '🎵', 'document': '📄', 'voice': '🎤'}[item.media_type] || '📎';
                    html += `<div style="border: 1px solid #ddd; padding: 15px; border-radius: 8px;">
                        <div style="font-size: 32px;">${icon}</div>
                        <div style="font-weight: bold; margin: 10px 0;">${item.file_name || 'Unnamed'}</div>
                        <div style="color: #666; font-size: 12px;">
                            Type: ${item.media_type}<br>
                            Size: ${formatBytes(item.file_size)}<br>
                            Chat: ${item.chat_name}
                        </div>
                        <div style="margin-top: 10px;">
                            ${item.media_type === 'video' ? `<button class="button" onclick="streamVideo(${item.id})">▶️ Stream</button>` : ''}
                            <button class="button" onclick="downloadMedia(${item.id})">⬇️ Download</button>
                        </div>
                    </div>`;
                });
                html += '</div>';
                document.getElementById('results-content').innerHTML = html;
            }
            
            function streamVideo(mediaId) {
                window.open(`/stream/${mediaId}`, '_blank');
            }
            
            async function downloadMedia(mediaId) {
                const response = await fetch(`/api/download/${mediaId}`, { method: 'POST' });
                const data = await response.json();
                alert(`Download queued! Queue ID: ${data.queue_id}`);
            }
            
            function formatBytes(bytes) {
                if (!bytes) return '0 B';
                const k = 1024;
                const sizes = ['B', 'KB', 'MB', 'GB'];
                const i = Math.floor(Math.log(bytes) / Math.log(k));
                return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
            }
            
            // Load stats on page load
            loadStats();
        </script>
    </body>
    </html>
    """


# API Endpoints

@app.get("/api/chats")
async def get_chats(
    limit: int = Query(100, ge=1, le=1000),
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


@app.get("/api/media/{media_id}")
async def get_media_by_id(media_id: int, db: AsyncSession = Depends(get_session)):
    """Get specific media"""
    result = await db.execute(
        select(Media).where(Media.id == media_id)
    )
    media = result.scalar_one_or_none()
    
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    return {
        'id': media.id,
        'message_id': media.message_id,
        'chat_id': media.chat_id,
        'file_name': media.file_name,
        'file_size': media.file_size,
        'media_type': media.media_type,
        'duration': media.duration,
        'width': media.width,
        'height': media.height,
        'mime_type': media.mime_type,
        'upload_date': media.upload_date.isoformat() if media.upload_date else None
    }


@app.get("/api/search")
async def search_media(
    q: Optional[str] = None,
    media_type: Optional[str] = None,
    chat_id: Optional[int] = None,
    min_size: Optional[int] = None,
    max_size: Optional[int] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_session)
):
    """Search media"""
    search_engine = SearchEngine(db)
    results = await search_engine.search_media(
        query=q,
        media_type=media_type,
        chat_id=chat_id,
        min_size=min_size,
        max_size=max_size,
        limit=limit,
        offset=offset
    )
    
    return [
        {
            'id': media.id,
            'message_id': media.message_id,
            'chat_id': media.chat_id,
            'chat_name': media.chat.name,
            'file_name': media.file_name,
            'file_size': media.file_size,
            'media_type': media.media_type,
            'upload_date': media.upload_date.isoformat() if media.upload_date else None
        }
        for media in results
    ]


@app.get("/api/stats")
async def get_stats(db: AsyncSession = Depends(get_session)):
    """Get statistics"""
    search_engine = SearchEngine(db)
    return await search_engine.get_stats()


@app.post("/api/scan/chats")
async def scan_chats(db: AsyncSession = Depends(get_session)):
    """Scan all chats"""
    scanner = MediaScanner(db)
    count = await scanner.scan_all_chats()
    return {'count': count}


@app.post("/api/scan/media")
async def scan_all_media(db: AsyncSession = Depends(get_session)):
    """Scan media from all chats"""
    scanner = MediaScanner(db)
    count = await scanner.scan_all_media()
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


@app.get("/api/messages")
async def get_messages(
    chat_id: Optional[int] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_session)
):
    """Get messages with filters"""
    query = select(Message).join(Chat)
    
    if chat_id:
        query = query.where(Message.chat_id == chat_id)
    
    if search:
        query = query.where(Message.text.ilike(f'%{search}%'))
    
    query = query.order_by(Message.date.desc()).limit(limit).offset(offset)
    
    result = await db.execute(query)
    messages = result.scalars().all()
    
    return [
        {
            'id': msg.id,
            'message_id': msg.message_id,
            'chat_id': msg.chat_id,
            'text': msg.text,
            'sender_id': msg.sender_id,
            'sender_name': msg.sender_name,
            'date': msg.date.isoformat() if msg.date else None,
            'reply_to_message_id': msg.reply_to_message_id,
            'forward_from': msg.forward_from,
            'has_media': msg.has_media
        }
        for msg in messages
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
            'created_at': item.created_at.isoformat()
        }
        for item in queue_items
    ]
