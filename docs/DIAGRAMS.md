# System Diagrams

Visual representations of the Telegram Media Server architecture and workflows.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Browser    │  │  Mobile App  │  │  API Client  │         │
│  │   (Chrome)   │  │   (Safari)   │  │   (Python)   │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
└─────────┼──────────────────┼──────────────────┼────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │ HTTP/REST
┌────────────────────────────▼─────────────────────────────────────┐
│                    APPLICATION LAYER                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              FastAPI Web Server (Port 8080)              │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │   │
│  │  │  REST API  │  │   HTML     │  │  WebSocket │        │   │
│  │  │ Endpoints  │  │ Dashboard  │  │  (Future)  │        │   │
│  │  └────────────┘  └────────────┘  └────────────┘        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  Business Logic Layer                    │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │   │
│  │  │   Scanner  │  │ Downloader │  │  Streamer  │        │   │
│  │  │   Engine   │  │   Engine   │  │   Engine   │        │   │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘        │   │
│  │        │                │                │               │   │
│  │  ┌─────▼──────┐  ┌─────▼──────┐  ┌─────▼──────┐        │   │
│  │  │   Search   │  │   Queue    │  │   Media    │        │   │
│  │  │   Engine   │  │  Manager   │  │  Processor │        │   │
│  │  └────────────┘  └────────────┘  └────────────┘        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Telegram Client (Telethon)                  │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │   │
│  │  │  Session   │  │   Dialog   │  │   Media    │        │   │
│  │  │  Manager   │  │   Handler  │  │   Handler  │        │   │
│  │  └────────────┘  └────────────┘  └────────────┘        │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────┬──────────────────┬───────────────────────┘
                        │                  │
        ┌───────────────▼──────┐  ┌────────▼────────────┐
        │   DATA LAYER         │  │  EXTERNAL SERVICES  │
        │  ┌────────────────┐  │  │  ┌──────────────┐  │
        │  │   Database     │  │  │  │   Telegram   │  │
        │  │ (SQLite/PG)    │  │  │  │   Servers    │  │
        │  └────────────────┘  │  │  └──────────────┘  │
        │  ┌────────────────┐  │  │                     │
        │  │  File Storage  │  │  │                     │
        │  │  (Downloads)   │  │  │                     │
        │  └────────────────┘  │  │                     │
        └──────────────────────┘  └─────────────────────┘
```

## Data Flow Diagrams

### Media Indexing Flow

```
┌──────────┐
│   User   │
└────┬─────┘
     │ 1. Click "Scan Media"
     ▼
┌─────────────────┐
│   Web Browser   │
└────┬────────────┘
     │ 2. POST /api/scan/media
     ▼
┌─────────────────┐
│   FastAPI       │
└────┬────────────┘
     │ 3. Call scanner.scan_all_media()
     ▼
┌─────────────────┐
│  Scanner Engine │
└────┬────────────┘
     │ 4. Get all chats from DB
     ▼
┌─────────────────┐
│   Database      │
└────┬────────────┘
     │ 5. Return chat list
     ▼
┌─────────────────┐
│  Scanner Engine │
└────┬────────────┘
     │ 6. For each chat...
     ▼
┌─────────────────┐
│ Telegram Client │
└────┬────────────┘
     │ 7. Get media messages
     ▼
┌─────────────────┐
│ Telegram Server │
└────┬────────────┘
     │ 8. Return messages
     ▼
┌─────────────────┐
│ Telegram Client │
└────┬────────────┘
     │ 9. Extract media metadata
     ▼
┌─────────────────┐
│  Scanner Engine │
└────┬────────────┘
     │ 10. Save to database
     ▼
┌─────────────────┐
│   Database      │
└────┬────────────┘
     │ 11. Update sync state
     ▼
┌─────────────────┐
│   FastAPI       │
└────┬────────────┘
     │ 12. Return count
     ▼
┌─────────────────┐
│   Web Browser   │
└────┬────────────┘
     │ 13. Display result
     ▼
┌──────────┐
│   User   │
└──────────┘
```

### Video Streaming Flow

```
┌──────────┐
│   User   │
└────┬─────┘
     │ 1. Click "Stream Video"
     ▼
┌─────────────────┐
│   Web Browser   │
└────┬────────────┘
     │ 2. GET /stream/{media_id}
     │    Range: bytes=0-1048575
     ▼
┌─────────────────┐
│   FastAPI       │
└────┬────────────┘
     │ 3. Get media info
     ▼
┌─────────────────┐
│   Database      │
└────┬────────────┘
     │ 4. Return media metadata
     ▼
┌─────────────────┐
│   FastAPI       │
└────┬────────────┘
     │ 5. Parse Range header
     │    Start: 0, End: 1048575
     ▼
┌─────────────────┐
│ Media Streamer  │
└────┬────────────┘
     │ 6. Request byte range
     ▼
┌─────────────────┐
│ Telegram Client │
└────┬────────────┘
     │ 7. Stream chunks
     ▼
┌─────────────────┐
│ Telegram Server │
└────┬────────────┘
     │ 8. Return data chunks
     ▼
┌─────────────────┐
│ Telegram Client │
└────┬────────────┘
     │ 9. Yield chunks
     ▼
┌─────────────────┐
│ Media Streamer  │
└────┬────────────┘
     │ 10. Stream to client
     ▼
┌─────────────────┐
│   FastAPI       │
└────┬────────────┘
     │ 11. HTTP 206 Partial Content
     │     Content-Range: bytes 0-1048575/10485760
     ▼
┌─────────────────┐
│   Web Browser   │
└────┬────────────┘
     │ 12. Play video chunk
     ▼
┌──────────┐
│   User   │ (Video plays)
└──────────┘
     │ 13. User seeks to 50%
     ▼
┌─────────────────┐
│   Web Browser   │
└────┬────────────┘
     │ 14. GET /stream/{media_id}
     │     Range: bytes=5242880-6291455
     ▼
     (Repeat from step 3)
```

### Download Flow

```
┌──────────┐
│   User   │
└────┬─────┘
     │ 1. Click "Download"
     ▼
┌─────────────────┐
│   Web Browser   │
└────┬────────────┘
     │ 2. POST /api/download/{media_id}
     ▼
┌─────────────────┐
│   FastAPI       │
└────┬────────────┘
     │ 3. Queue download
     ▼
┌─────────────────┐
│ Download Engine │
└────┬────────────┘
     │ 4. Add to queue
     ▼
┌─────────────────┐
│   Database      │
└────┬────────────┘
     │ 5. Insert queue item
     │    Status: pending
     ▼
┌─────────────────┐
│   FastAPI       │
└────┬────────────┘
     │ 6. Return queue_id
     ▼
┌─────────────────┐
│   Web Browser   │
└────┬────────────┘
     │ 7. Show "Queued"
     ▼
┌──────────┐
│   User   │
└──────────┘

(Background Process)

┌─────────────────┐
│ Download Worker │
└────┬────────────┘
     │ 1. Check queue
     ▼
┌─────────────────┐
│   Database      │
└────┬────────────┘
     │ 2. Get pending item
     ▼
┌─────────────────┐
│ Download Worker │
└────┬────────────┘
     │ 3. Update status: downloading
     ▼
┌─────────────────┐
│   Database      │
└────┬────────────┘
     │ 4. Get media info
     ▼
┌─────────────────┐
│ Download Worker │
└────┬────────────┘
     │ 5. Download media
     ▼
┌─────────────────┐
│ Telegram Client │
└────┬────────────┘
     │ 6. Request file
     ▼
┌─────────────────┐
│ Telegram Server │
└────┬────────────┘
     │ 7. Stream file data
     ▼
┌─────────────────┐
│ Telegram Client │
└────┬────────────┘
     │ 8. Write to disk
     │    /data/downloads/channels/...
     ▼
┌─────────────────┐
│  File System    │
└────┬────────────┘
     │ 9. File saved
     ▼
┌─────────────────┐
│ Download Worker │
└────┬────────────┘
     │ 10. Update status: completed
     │     Update media.downloaded = true
     ▼
┌─────────────────┐
│   Database      │
└─────────────────┘
```

## Component Interaction

```
┌─────────────────────────────────────────────────────────┐
│                    Web API Layer                        │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │  Chats   │  │  Media   │  │  Search  │             │
│  │   API    │  │   API    │  │   API    │             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
└───────┼─────────────┼─────────────┼────────────────────┘
        │             │             │
        ▼             ▼             ▼
┌─────────────────────────────────────────────────────────┐
│                  Service Layer                          │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Scanner  │  │Downloader│  │ Streamer │             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
│       │             │             │                     │
│  ┌────▼─────────────▼─────────────▼─────┐             │
│  │        Search Engine                  │             │
│  └───────────────────┬───────────────────┘             │
└────────────────────────┼───────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Database   │  │   Telegram   │  │     File     │
│    Layer     │  │    Client    │  │    System    │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Database Schema

```
┌─────────────────────┐
│       chats         │
├─────────────────────┤
│ id (PK)             │◄──┐
│ name                │   │
│ username            │   │
│ chat_type           │   │
│ member_count        │   │
│ last_activity       │   │
│ created_at          │   │
│ updated_at          │   │
└─────────────────────┘   │
                          │
                          │ FK
┌─────────────────────┐   │
│       media         │   │
├─────────────────────┤   │
│ id (PK)             │   │
│ message_id          │   │
│ chat_id (FK)        │───┘
│ file_name           │
│ file_size           │
│ media_type          │
│ duration            │
│ width               │
│ height              │
│ mime_type           │
│ upload_date         │
│ downloaded          │
│ download_path       │
└─────────────────────┘
         ▲
         │ FK
         │
┌─────────────────────┐
│   download_queue    │
├─────────────────────┤
│ id (PK)             │
│ media_id (FK)       │───┘
│ status              │
│ progress            │
│ error_message       │
│ created_at          │
│ started_at          │
│ completed_at        │
└─────────────────────┘

┌─────────────────────┐
│    sync_state       │
├─────────────────────┤
│ id (PK)             │
│ chat_id (UNIQUE)    │
│ last_message_id     │
│ last_sync           │
│ total_messages      │
│ total_media         │
└─────────────────────┘
```

## Deployment Architecture

### Single Server Deployment

```
┌─────────────────────────────────────────────┐
│           Docker Host                       │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │  telegram-media-server Container      │ │
│  │                                       │ │
│  │  ┌─────────────────────────────────┐ │ │
│  │  │  Python Application             │ │ │
│  │  │  - FastAPI                      │ │ │
│  │  │  - Telethon                     │ │ │
│  │  │  - Background Workers           │ │ │
│  │  └─────────────────────────────────┘ │ │
│  │                                       │ │
│  │  Port 8080 ───────────────────────────┼─┼──► Internet
│  │                                       │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │  Docker Volumes                       │ │
│  │  - ./data/session                     │ │
│  │  - ./data/database                    │ │
│  │  - ./data/downloads                   │ │
│  └───────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### Production Deployment with PostgreSQL

```
┌─────────────────────────────────────────────────────────┐
│                   Docker Host                           │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  telegram-media-server Container                   │ │
│  │  Port 8080 ─────────────────────────────────────────┼─┼──► Internet
│  └────────────────┬───────────────────────────────────┘ │
│                   │                                      │
│                   │ Database Connection                  │
│                   ▼                                      │
│  ┌────────────────────────────────────────────────────┐ │
│  │  postgres Container                                │ │
│  │  Port 5432 (internal)                              │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Docker Volumes                                    │ │
│  │  - ./data/session                                  │ │
│  │  - ./data/downloads                                │ │
│  │  - postgres_data                                   │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Scalable Deployment (Future)

```
┌─────────────────────────────────────────────────────────┐
│                   Load Balancer                         │
│                   (Nginx/Caddy)                         │
└────────┬────────────────────────────────────┬───────────┘
         │                                    │
    ┌────▼────┐                          ┌────▼────┐
    │  API    │                          │  API    │
    │ Server  │                          │ Server  │
    │   #1    │                          │   #2    │
    └────┬────┘                          └────┬────┘
         │                                    │
         └────────────────┬───────────────────┘
                          │
              ┌───────────┼───────────┐
              │           │           │
         ┌────▼────┐ ┌────▼────┐ ┌───▼─────┐
         │ Postgres│ │  Redis  │ │ Shared  │
         │Database │ │  Queue  │ │ Storage │
         └─────────┘ └─────────┘ └─────────┘
```

## State Machine: Download Queue

```
┌─────────┐
│ PENDING │
└────┬────┘
     │ Worker picks up
     ▼
┌──────────────┐
│ DOWNLOADING  │
└────┬─────────┘
     │
     ├─── Success ───► ┌───────────┐
     │                 │ COMPLETED │
     │                 └───────────┘
     │
     └─── Failure ───► ┌─────────┐
                       │ FAILED  │
                       └────┬────┘
                            │ Retry
                            ▼
                       ┌─────────┐
                       │ PENDING │
                       └─────────┘
```

## Request Flow Timeline

```
Time →

User Action:     [Click Scan]
                      │
Browser:              ├─► [POST Request]
                      │         │
API:                  │         ├─► [Validate]
                      │         │       │
Scanner:              │         │       ├─► [Get Chats]
                      │         │       │       │
Database:             │         │       │       ├─► [Query]
                      │         │       │       │      │
                      │         │       │       │      └─► [Return]
Scanner:              │         │       │       ├─◄ [Process]
                      │         │       │       │
Telegram:             │         │       │       ├─► [Fetch Messages]
                      │         │       │       │         │
                      │         │       │       │         └─► [Return]
Scanner:              │         │       │       ├─◄ [Extract Media]
                      │         │       │       │
Database:             │         │       │       ├─► [Save]
                      │         │       │       │      │
                      │         │       │       │      └─► [OK]
API:                  │         │       ├─◄ [Complete]
                      │         │       │
Browser:              │         ├─◄ [Response]
                      │         │
User:                 ├─◄ [Display Result]
                      │
                   [Done]
```

These diagrams provide a visual understanding of how the Telegram Media Server works internally and how different components interact with each other.
