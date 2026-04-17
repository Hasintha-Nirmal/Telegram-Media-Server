# Architecture Documentation

## System Overview

The Telegram Media Server is a self-hosted cloud storage system that uses your Telegram account as the backend. It provides a web interface for browsing, searching, streaming, and downloading media from all your Telegram chats.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Web Browser                          │
│                    (User Interface)                         │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Server                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Web API    │  │  Streaming   │  │  Downloads   │     │
│  │  Endpoints   │  │   Handler    │  │    Queue     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Scanner   │  │  Downloader │  │   Search    │
│   Engine    │  │   Engine    │  │   Engine    │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┼────────────────┘
                        ▼
              ┌──────────────────┐
              │ Telegram Client  │
              │   (Telethon)     │
              └────────┬─────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼                           ▼
┌──────────────┐            ┌──────────────┐
│   Database   │            │   Telegram   │
│  (SQLite/    │            │   Servers    │
│  PostgreSQL) │            │              │
└──────────────┘            └──────────────┘
```

## Core Components

### 1. Telegram Client (`app/telegram_client.py`)

Handles all communication with Telegram servers using Telethon.

Features:
- Session-based authentication
- Dialog (chat) discovery
- Media message retrieval
- Media streaming with byte-range support
- Media downloading

Key Methods:
- `connect()`: Establish connection using session file
- `get_dialogs()`: Retrieve all chats
- `get_media_messages()`: Fetch media from a chat
- `stream_media()`: Stream media in chunks
- `download_media()`: Download media to disk

### 2. Scanner Engine (`app/scanner.py`)

Discovers and indexes chats and media.

Features:
- Chat discovery and metadata extraction
- Incremental media scanning
- Sync state tracking
- Batch processing

Workflow:
1. Scan all dialogs from Telegram
2. Save chat metadata to database
3. For each chat, iterate through messages
4. Extract media information
5. Store media metadata in database
6. Track last scanned message ID

### 3. Search Engine (`app/search_engine.py`)

Provides powerful search and filtering capabilities.

Features:
- Full-text search on filenames and chat names
- Filter by media type
- Filter by file size range
- Filter by date range
- Filter by chat
- Statistics aggregation

### 4. Downloader Engine (`app/downloader.py`)

Manages media downloads with queue system.

Features:
- Download queue management
- Parallel downloads (configurable)
- Progress tracking
- Automatic file organization
- Retry on failure

File Organization:
```
/data/downloads/
├── channels/
│   └── channel_name/
│       └── video.mp4
├── groups/
│   └── group_name/
│       └── photo.jpg
├── users/
│   └── username/
│       └── document.pdf
└── bots/
    └── bot_name/
        └── audio.mp3
```

### 5. Media Streamer (`app/streamer.py`)

Enables direct streaming from Telegram without full download.

Features:
- HTTP range request support
- Progressive streaming
- Byte-range seeking
- Compatible with HTML5 video players

How it works:
1. Client requests media with optional Range header
2. Streamer fetches requested byte range from Telegram
3. Returns partial content (206) or full content (200)
4. Video players can seek without downloading entire file

### 6. Web API (`web/api.py`)

RESTful API built with FastAPI.

Endpoints:
- `/api/chats` - List all chats
- `/api/media` - List media with filters
- `/api/search` - Search media
- `/api/stats` - Get statistics
- `/api/scan/*` - Trigger scanning
- `/api/download/*` - Queue downloads
- `/stream/{id}` - Stream media

### 7. Database Layer (`database/`)

SQLAlchemy models with async support.

Tables:
- `chats` - Chat metadata
- `media` - Media metadata and references
- `download_queue` - Download queue items
- `sync_state` - Incremental sync tracking

## Data Flow

### Media Indexing Flow

```
User clicks "Scan Media"
    ↓
API receives POST /api/scan/media
    ↓
Scanner.scan_all_chats()
    ↓
For each chat:
    ↓
    TelegramClient.get_media_messages()
    ↓
    Extract media metadata
    ↓
    Save to database
    ↓
    Update sync state
    ↓
Return total count
```

### Streaming Flow

```
User clicks "Stream Video"
    ↓
Browser requests GET /stream/{media_id}
    ↓
API fetches media info from database
    ↓
Parse Range header (if present)
    ↓
TelegramClient.stream_media(offset, limit)
    ↓
Yield chunks to client
    ↓
Browser plays video progressively
```

### Download Flow

```
User clicks "Download"
    ↓
API receives POST /api/download/{media_id}
    ↓
Downloader.queue_download()
    ↓
Add to download_queue table
    ↓
Background worker picks up job
    ↓
TelegramClient.download_media()
    ↓
Save to organized folder structure
    ↓
Update media.downloaded = True
    ↓
Update queue status = "completed"
```

## Background Tasks

### Auto-Sync Task

Runs every N seconds (configurable via `SYNC_INTERVAL`).

Process:
1. Scan for new chats
2. For each chat, scan for new media since last sync
3. Update database with new media
4. Update sync state

This ensures the index stays up-to-date with new Telegram messages.

## Database Schema

### Chats Table
```sql
CREATE TABLE chats (
    id BIGINT PRIMARY KEY,
    name VARCHAR NOT NULL,
    username VARCHAR,
    chat_type VARCHAR NOT NULL,
    member_count INTEGER,
    last_activity TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Media Table
```sql
CREATE TABLE media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id BIGINT NOT NULL,
    chat_id BIGINT REFERENCES chats(id),
    file_name VARCHAR,
    file_size BIGINT,
    media_type VARCHAR NOT NULL,
    duration INTEGER,
    width INTEGER,
    height INTEGER,
    mime_type VARCHAR,
    file_reference VARCHAR,
    upload_date TIMESTAMP,
    created_at TIMESTAMP,
    downloaded BOOLEAN DEFAULT FALSE,
    download_path VARCHAR
);
```

### Download Queue Table
```sql
CREATE TABLE download_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    media_id INTEGER REFERENCES media(id),
    status VARCHAR DEFAULT 'pending',
    progress FLOAT DEFAULT 0.0,
    error_message VARCHAR,
    created_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

### Sync State Table
```sql
CREATE TABLE sync_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id BIGINT UNIQUE NOT NULL,
    last_message_id BIGINT,
    last_sync TIMESTAMP,
    total_messages INTEGER DEFAULT 0,
    total_media INTEGER DEFAULT 0
);
```

## Performance Considerations

### Indexing Strategy

Database indexes on:
- `media.chat_id` - Fast filtering by chat
- `media.media_type` - Fast filtering by type
- `media.file_name` - Fast text search
- `media.upload_date` - Fast date range queries
- `chats.chat_type` - Fast filtering by chat type

### Streaming Optimization

- Chunk-based streaming (no full download required)
- Range request support for seeking
- Async I/O for concurrent streams
- Direct Telegram API streaming (no local caching)

### Scanning Optimization

- Incremental scanning (only new messages)
- Sync state tracking per chat
- Batch database inserts
- Async message iteration

### Download Optimization

- Parallel downloads (configurable limit)
- Queue-based system prevents overload
- Progress tracking
- Automatic retry on failure

## Scalability

### Horizontal Scaling

To scale horizontally:
1. Use PostgreSQL instead of SQLite
2. Add Redis for queue management
3. Deploy multiple API instances behind load balancer
4. Use shared storage for downloads (NFS, S3)

### Vertical Scaling

- Increase `MAX_PARALLEL_DOWNLOADS`
- Increase database connection pool
- Add more CPU cores for concurrent requests
- Increase memory for larger caches

## Security Considerations

### Session Security

- Session file provides full account access
- Store securely with restricted permissions
- Never expose in logs or API responses
- Rotate periodically

### API Security

Current implementation has no authentication. For production:
- Add JWT authentication
- Implement rate limiting
- Use HTTPS only
- Add CORS restrictions
- Implement user roles

### Data Privacy

- All data stays on your server
- No third-party services
- Telegram E2E encrypted chats not accessible
- Local database encryption optional

## Deployment Options

### Docker (Recommended)

Single container with SQLite:
```bash
docker-compose up -d
```

Multi-container with PostgreSQL:
```bash
docker-compose -f docker-compose.postgres.yml up -d
```

### Kubernetes

Create deployments for:
- API server (multiple replicas)
- Background worker (sync task)
- PostgreSQL (StatefulSet)
- Redis (optional, for queue)

### Bare Metal

```bash
pip install -r requirements.txt
python main.py
```

## Monitoring

### Logs

Application logs include:
- Connection status
- Scan progress
- Download status
- API requests
- Errors and exceptions

### Metrics

Track:
- Total chats indexed
- Total media indexed
- Storage usage
- API request rate
- Download queue length
- Sync task duration

### Health Checks

Implement:
- `/health` endpoint
- Database connectivity check
- Telegram connection check
- Disk space check

## Future Enhancements

Potential features:
- User authentication system
- Multi-user support
- Advanced search (fuzzy, full-text)
- Thumbnail generation
- Video transcoding
- Mobile app
- Sharing links
- Collections/playlists
- Duplicate detection
- Automatic tagging
- Face recognition
- OCR for documents
