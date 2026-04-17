# Setup Guide

## Prerequisites

1. Python 3.11+ (for local development)
2. Docker and Docker Compose (for production)
3. Telegram API credentials (API_ID and API_HASH)
4. Valid Telegram session file

## Getting Telegram API Credentials

1. Go to https://my.telegram.org
2. Log in with your phone number
3. Go to "API development tools"
4. Create a new application
5. Copy your `api_id` and `api_hash`

## Creating a Session File

You need to create a Telegram session file before running the server.

### Option 1: Using Telethon Script

Create a file `create_session.py`:

```python
from telethon import TelegramClient

API_ID = 'your_api_id'
API_HASH = 'your_api_hash'
SESSION_NAME = 'account'

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

async def main():
    await client.start()
    print("Session created successfully!")
    await client.disconnect()

with client:
    client.loop.run_until_complete(main())
```

Run it:
```bash
python create_session.py
```

This will create `account.session` file. Move it to `./data/session/`

### Option 2: Using Existing Session

If you already have a session file from another Telethon application, copy it to:
```
./data/session/account.session
```

## Installation

### Docker (Recommended)

1. Clone the repository
2. Create `.env` file:
```bash
cp .env.example .env
```

3. Edit `.env` with your credentials:
```
API_ID=12345678
API_HASH=your_api_hash_here
SESSION_PATH=/data/session/account.session
```

4. Place your session file:
```bash
mkdir -p data/session
cp /path/to/your/account.session data/session/
```

5. Start the server:
```bash
docker-compose up -d
```

6. Access the web interface:
```
http://localhost:8080
```

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file and configure

3. Place session file in `./data/session/`

4. Run the server:
```bash
python main.py
```

## First Time Setup

1. Access http://localhost:8080
2. Click "Scan Chats" to discover all your Telegram chats
3. Click "Scan All Media" to index media (this may take a while for large accounts)
4. Browse, search, and stream your media!

## Configuration

All configuration is done via environment variables in `.env`:

- `API_ID`: Your Telegram API ID (required)
- `API_HASH`: Your Telegram API Hash (required)
- `SESSION_PATH`: Path to session file (default: /data/session/account.session)
- `DATABASE_URL`: Database connection string (default: SQLite)
- `DOWNLOAD_PATH`: Where to store downloaded files (default: /data/downloads)
- `SYNC_INTERVAL`: Auto-sync interval in seconds (default: 600)
- `MAX_PARALLEL_DOWNLOADS`: Max concurrent downloads (default: 3)

## Troubleshooting

### "Session is not authorized"
- Your session file is invalid or expired
- Create a new session file using the script above

### "Connection failed"
- Check your internet connection
- Verify API_ID and API_HASH are correct
- Ensure session file exists and is readable

### "Database locked"
- SQLite doesn't handle high concurrency well
- Consider using PostgreSQL for production

### Media not streaming
- Check that the media still exists in Telegram
- Verify file permissions on data directories
- Check Docker logs: `docker-compose logs -f`

## Upgrading

```bash
docker-compose down
docker-compose pull
docker-compose up -d
```

## Backup

Important files to backup:
- `./data/session/` - Your Telegram session
- `./data/database/` - Media index database
- `./data/downloads/` - Downloaded files

## Security Notes

- Keep your session file secure - it provides full access to your Telegram account
- Don't expose the server to the internet without authentication
- Use HTTPS in production
- Consider adding authentication middleware
