# Project Structure

```
telegram-media-server/
│
├── app/                          # Core application logic
│   ├── __init__.py
│   ├── config.py                 # Configuration management
│   ├── telegram_client.py        # Telegram API client (Telethon)
│   ├── scanner.py                # Chat and media scanner
│   ├── downloader.py             # Download queue manager
│   ├── streamer.py               # Media streaming handler
│   └── search_engine.py          # Search and filter engine
│
├── database/                     # Database layer
│   ├── __init__.py               # Database initialization
│   └── models.py                 # SQLAlchemy models
│
├── web/                          # Web interface
│   ├── __init__.py
│   └── api.py                    # FastAPI application and endpoints
│
├── scripts/                      # Utility scripts
│   ├── create_session.py         # Create Telegram session
│   └── migrate_postgres.py       # Migrate to PostgreSQL
│
├── data/                         # Persistent data (created at runtime)
│   ├── session/                  # Telegram session files
│   │   └── account.session
│   ├── database/                 # SQLite database
│   │   └── media.db
│   └── downloads/                # Downloaded media files
│       ├── channels/
│       ├── groups/
│       ├── users/
│       └── bots/
│
├── main.py                       # Application entry point
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker image definition
├── docker-compose.yml            # Docker Compose (SQLite)
├── docker-compose.postgres.yml  # Docker Compose (PostgreSQL)
│
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
│
├── README.md                     # Project overview
├── QUICKSTART.md                 # Quick start guide
├── SETUP.md                      # Detailed setup instructions
├── API.md                        # API documentation
├── ARCHITECTURE.md               # Architecture documentation
└── PROJECT_STRUCTURE.md          # This file
```

## File Descriptions

### Core Application (`app/`)

**config.py**
- Loads environment variables
- Provides settings object
- Validates configuration

**telegram_client.py**
- Wraps Telethon client
- Handles Telegram authentication
- Provides methods for:
  - Getting dialogs (chats)
  - Fetching media messages
  - Streaming media
  - Downloading media

**scanner.py**
- Discovers all chats
- Scans messages for media
- Extracts media metadata
- Implements incremental scanning
- Tracks sync state

**downloader.py**
- Manages download queue
- Handles parallel downloads
- Tracks download progress
- Organizes files by chat type
- Implements retry logic

**streamer.py**
- Streams media from Telegram
- Supports HTTP range requests
- Enables progressive video playback
- No local caching required

**search_engine.py**
- Searches media by name
- Filters by type, size, date
- Provides statistics
- Optimized database queries

### Database Layer (`database/`)

**models.py**
- Defines SQLAlchemy models:
  - `Chat`: Chat metadata
  - `Media`: Media metadata
  - `DownloadQueue`: Download jobs
  - `SyncState`: Incremental sync tracking
- Includes indexes for performance

**__init__.py**
- Creates async database engine
- Provides session factory
- Initializes database tables

### Web Interface (`web/`)

**api.py**
- FastAPI application
- REST API endpoints
- HTML dashboard
- Request/response handling
- Error handling

### Scripts (`scripts/`)

**create_session.py**
- Interactive script to create Telegram session
- Handles phone verification
- Saves session file

**migrate_postgres.py**
- Migrates from SQLite to PostgreSQL
- Creates tables in PostgreSQL
- Provides migration instructions

### Configuration Files

**.env.example**
- Template for environment variables
- Documents all configuration options
- Safe to commit (no secrets)

**requirements.txt**
- Python package dependencies
- Pinned versions for reproducibility

**Dockerfile**
- Defines Docker image
- Based on Python 3.11
- Installs dependencies
- Sets up application

**docker-compose.yml**
- Single-container deployment
- Uses SQLite database
- Mounts data volumes
- Exposes port 8080

**docker-compose.postgres.yml**
- Multi-container deployment
- Includes PostgreSQL service
- Better for production
- Persistent database volume

### Documentation

**README.md**
- Project overview
- Feature list
- Quick links

**QUICKSTART.md**
- 5-minute setup guide
- Step-by-step instructions
- Common commands

**SETUP.md**
- Detailed setup instructions
- Configuration options
- Troubleshooting guide

**API.md**
- Complete API reference
- Request/response examples
- Usage examples in multiple languages

**ARCHITECTURE.md**
- System architecture
- Component descriptions
- Data flow diagrams
- Performance considerations
- Scalability options

## Data Flow

```
User Request
    ↓
web/api.py (FastAPI)
    ↓
app/* (Business Logic)
    ↓
database/models.py (Data Layer)
    ↓
SQLite/PostgreSQL
```

```
Telegram API
    ↓
app/telegram_client.py (Telethon)
    ↓
app/scanner.py (Processing)
    ↓
database/models.py (Storage)
    ↓
SQLite/PostgreSQL
```

## Module Dependencies

```
main.py
  └── web/api.py
      ├── app/telegram_client.py
      ├── app/scanner.py
      ├── app/downloader.py
      ├── app/streamer.py
      ├── app/search_engine.py
      └── database/
          ├── __init__.py
          └── models.py
```

## Key Design Patterns

**Singleton Pattern**
- `telegram_client` is a global singleton
- Ensures single Telegram connection

**Repository Pattern**
- Database models separate from business logic
- Clean separation of concerns

**Queue Pattern**
- Download queue for async processing
- Prevents overload

**Streaming Pattern**
- Generator-based streaming
- Memory efficient

**Factory Pattern**
- Session factory for database connections
- Proper resource management

## Extension Points

To add new features:

1. **New media type**: Update `telegram_client._extract_media_info()`
2. **New API endpoint**: Add to `web/api.py`
3. **New search filter**: Update `search_engine.search_media()`
4. **New background task**: Add to `main.py`
5. **New database table**: Add model to `database/models.py`

## Testing Structure (Future)

```
tests/
├── unit/
│   ├── test_scanner.py
│   ├── test_downloader.py
│   └── test_search.py
├── integration/
│   ├── test_api.py
│   └── test_telegram.py
└── fixtures/
    └── sample_data.py
```

## Deployment Structure

```
Production Server
├── Docker Container (telegram-media-server)
│   ├── Python Application
│   └── Uvicorn Server
├── Docker Container (postgres) [optional]
│   └── PostgreSQL Database
└── Docker Volumes
    ├── session/
    ├── database/
    └── downloads/
```
