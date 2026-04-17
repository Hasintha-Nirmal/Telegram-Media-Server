# Quick Start Guide

Get your Telegram Media Server running in 5 minutes!

## Step 1: Get Telegram API Credentials

1. Visit https://my.telegram.org
2. Log in with your phone number
3. Click "API development tools"
4. Fill in the form (app name can be anything)
5. Copy your `api_id` and `api_hash`

## Step 2: Create Session File

Install Telethon locally:
```bash
pip install telethon
```

Run this Python script:
```python
from telethon import TelegramClient

API_ID = 12345678  # Your api_id
API_HASH = 'your_api_hash_here'

client = TelegramClient('account', API_ID, API_HASH)

async def main():
    await client.start()
    print("✅ Session created!")
    me = await client.get_me()
    print(f"Logged in as: {me.first_name}")

with client:
    client.loop.run_until_complete(main())
```

This creates `account.session` file in the current directory.

## Step 3: Setup Project

Clone or download the project:
```bash
cd telegram-media-server
```

Create data directory and move session:
```bash
mkdir -p data/session
mv /path/to/account.session data/session/
```

Create `.env` file:
```bash
cat > .env << EOF
API_ID=12345678
API_HASH=your_api_hash_here
SESSION_PATH=/data/session/account.session
DATABASE_URL=sqlite:////data/database/media.db
DOWNLOAD_PATH=/data/downloads
SYNC_INTERVAL=600
MAX_PARALLEL_DOWNLOADS=3
EOF
```

## Step 4: Start Server

Using Docker (recommended):
```bash
docker-compose up -d
```

Or locally:
```bash
pip install -r requirements.txt
python main.py
```

## Step 5: Access Web Interface

Open your browser:
```
http://localhost:8080
```

## Step 6: Index Your Media

1. Click "🔍 Scan Chats" button
   - This discovers all your Telegram chats
   - Takes a few seconds

2. Click "📥 Scan All Media" button
   - This indexes all media from your chats
   - May take several minutes depending on your account size
   - You can monitor progress in the logs

3. Wait for scanning to complete

## Step 7: Start Using!

Now you can:

- **Browse Media**: Click "🎬 View Media" to see all indexed media
- **Search**: Use the search box to find specific files
- **Stream Videos**: Click "▶️ Stream" on any video to watch in browser
- **Download**: Click "⬇️ Download" to save files locally
- **Filter**: Use the media type dropdown to filter by type

## Common Commands

View logs:
```bash
docker-compose logs -f
```

Stop server:
```bash
docker-compose down
```

Restart server:
```bash
docker-compose restart
```

Update server:
```bash
docker-compose down
docker-compose pull
docker-compose up -d
```

## Troubleshooting

### "Session is not authorized"
Your session file is invalid. Create a new one using Step 2.

### "Connection refused"
Server isn't running. Check with `docker-compose ps`

### "No media found"
You need to scan first. Click "Scan Chats" then "Scan All Media"

### Slow scanning
This is normal for accounts with many chats. The system scans incrementally, so subsequent scans are faster.

## What's Next?

- Read [SETUP.md](SETUP.md) for detailed configuration
- Check [API.md](API.md) for API documentation
- See [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
- Enable auto-sync to keep media index updated automatically

## Tips

1. **Auto-sync**: The server automatically scans for new media every 10 minutes (configurable)

2. **Incremental scanning**: After the first full scan, subsequent scans only check for new messages

3. **Streaming vs Downloading**: 
   - Streaming: Watch immediately without downloading
   - Downloading: Save to disk for offline access

4. **Organization**: Downloaded files are automatically organized by chat type and name

5. **Search**: Search works on both file names and chat names

6. **Performance**: For large accounts (100k+ media), consider using PostgreSQL instead of SQLite

## Example Workflow

1. Scan chats and media (first time setup)
2. Search for "vacation" to find vacation videos
3. Stream videos directly in browser
4. Download favorites for offline viewing
5. Let auto-sync keep everything updated
6. Use API to integrate with other tools

Enjoy your personal Telegram media cloud! 🚀
