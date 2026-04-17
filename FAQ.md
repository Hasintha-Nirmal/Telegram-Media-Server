# Frequently Asked Questions (FAQ)

## General Questions

### What is Telegram Media Server?

A self-hosted application that turns your Telegram account into a personal cloud storage system. It indexes all media from your chats and provides a web interface similar to Seedr for browsing, searching, streaming, and downloading.

### Is this official Telegram software?

No, this is a third-party tool that uses Telegram's official API through the Telethon library.

### Is it free?

Yes, completely free and open source. You only need a server to host it (can be your own computer).

### Do I need Telegram Premium?

No, works with regular Telegram accounts. Premium accounts have higher file size limits (4GB vs 2GB).

## Setup & Installation

### What do I need to get started?

1. Telegram account
2. API credentials from https://my.telegram.org
3. Docker installed (or Python 3.11+)
4. A session file from your Telegram account

### How do I get API credentials?

1. Go to https://my.telegram.org
2. Log in with your phone number
3. Click "API development tools"
4. Create an application
5. Copy your `api_id` and `api_hash`

### How do I create a session file?

Use the provided script:
```bash
python scripts/create_session.py
```

Or use Telethon directly:
```python
from telethon import TelegramClient
client = TelegramClient('account', API_ID, API_HASH)
client.start()
```

### Can I use an existing session file?

Yes! If you have a session file from another Telethon application, just copy it to `./data/session/`

### Do I need to keep Telegram Desktop running?

No, the server connects independently using your session file.

## Features & Functionality

### What media types are supported?

- Videos (MP4, MKV, AVI, MOV, WebM, etc.)
- Photos (JPG, PNG, GIF, WebP)
- Audio (MP3, WAV, OGG, FLAC)
- Documents (PDF, DOC, ZIP, etc.)
- Voice messages
- GIFs

### Can I stream videos without downloading?

Yes! Videos stream directly from Telegram with seeking support, just like YouTube or Netflix.

### How does streaming work?

The server fetches video chunks from Telegram on-demand using HTTP range requests. Your browser plays the video progressively without downloading the entire file.

### Can I download files?

Yes, you can download any media to your server. Files are automatically organized by chat type and name.

### Does it work with private chats?

Yes, it indexes media from all chat types: channels, groups, supergroups, private chats, and bots.

### Can I search for media?

Yes, you can search by:
- Filename
- Chat name
- Media type
- File size
- Upload date

### How often does it sync new media?

By default, every 10 minutes. Configurable via `SYNC_INTERVAL` in .env file.

## Performance & Limits

### How long does initial scanning take?

Depends on your account size:
- Small account (few chats, <1000 media): 1-5 minutes
- Medium account (50+ chats, 5000+ media): 10-30 minutes
- Large account (100+ chats, 50000+ media): 1-3 hours

Subsequent scans are much faster (incremental).

### What are the file size limits?

Limited by Telegram:
- Regular accounts: 2GB per file
- Premium accounts: 4GB per file

### How much storage do I need?

For the database:
- ~1KB per media item
- 10,000 media = ~10MB database

For downloads:
- Depends on what you download
- Only downloaded files use disk space
- Streaming doesn't require local storage

### Can it handle large accounts?

Yes! Tested with:
- 100+ chats
- 50,000+ media items
- Works smoothly with proper configuration

For very large accounts, use PostgreSQL instead of SQLite.

### Will it slow down my Telegram?

No, it doesn't affect your Telegram usage at all. It's a separate connection.

## Security & Privacy

### Is my data safe?

Yes, everything runs on your server. No data is sent to third parties.

### Who can access my media?

Only people with access to your server. The current version has no authentication, so add a reverse proxy with auth for internet exposure.

### Can others see my private chats?

Only if they have access to your server. Keep your server secure.

### What about the session file?

The session file provides full access to your Telegram account. Keep it secure:
- Don't share it
- Set proper file permissions (600)
- Back it up securely
- Rotate periodically

### Does it store my password?

No, it uses session-based authentication. No passwords are stored.

### Can Telegram ban my account?

Unlikely if you follow Telegram's Terms of Service. The tool uses official APIs and respects rate limits. Don't abuse it.

## Technical Questions

### What technology stack is used?

- Backend: Python 3.11, FastAPI, Telethon
- Database: SQLite (default) or PostgreSQL
- Frontend: HTML5, JavaScript
- Deployment: Docker

### Can I use PostgreSQL instead of SQLite?

Yes! Use the PostgreSQL docker-compose file:
```bash
docker-compose -f docker-compose.postgres.yml up -d
```

### Can I run it without Docker?

Yes:
```bash
pip install -r requirements.txt
python main.py
```

### What ports does it use?

- 8080: Web interface and API (configurable)
- 5432: PostgreSQL (if using postgres compose file)

### Can I change the port?

Yes, edit docker-compose.yml:
```yaml
ports:
  - "3000:8080"  # Access on port 3000
```

### Does it support HTTPS?

Not built-in. Use a reverse proxy like Nginx or Caddy:
```nginx
server {
    listen 443 ssl;
    server_name media.example.com;
    
    location / {
        proxy_pass http://localhost:8080;
    }
}
```

### Can I run multiple instances?

Yes, but each needs:
- Different port
- Different data directory
- Different session file (different account)

### Does it support multiple users?

Not currently. Each instance is for one Telegram account. Multi-user support is a future feature.

## Usage Questions

### How do I scan for new media?

Two ways:
1. Automatic: Runs every 10 minutes (configurable)
2. Manual: Click "Scan All Media" in web interface

### Can I scan specific chats only?

Yes, use the API:
```bash
curl -X POST http://localhost:8080/api/scan/chat/CHAT_ID
```

### How do I organize downloads?

Files are automatically organized:
```
downloads/
├── channels/channel_name/
├── groups/group_name/
├── users/username/
└── bots/bot_name/
```

### Can I download entire chats?

Not yet through UI, but you can use the API or implement it.

### How do I backup my data?

Backup these directories:
```bash
cp -r data/session data/session.backup
cp -r data/database data/database.backup
cp -r data/downloads data/downloads.backup
```

### Can I export the database?

Yes, it's just SQLite or PostgreSQL. Use standard database tools.

### How do I update the server?

```bash
docker-compose down
docker-compose pull
docker-compose up -d
```

## Troubleshooting

### Why can't I connect?

Common causes:
- Invalid session file
- Wrong API credentials
- Network/firewall issues
- Telegram blocked in your region

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for solutions.

### Why is scanning slow?

- Normal for first scan
- Large number of messages
- Telegram rate limits
- Server resources

### Why won't videos play?

- Browser compatibility
- Media format not supported
- File no longer in Telegram
- Network issues

### Database is locked?

SQLite doesn't handle concurrency well. Use PostgreSQL for production.

## Comparison Questions

### How is this different from Telegram Desktop?

- Web interface accessible from anywhere
- Powerful search across all chats
- Video streaming without download
- Organized media library
- API for automation

### How is this different from Seedr?

- Self-hosted (you control everything)
- Free (no subscription)
- Uses Telegram as storage backend
- No torrent support (yet)
- Single-user (currently)

### How is this different from cloud storage?

- Uses Telegram's infrastructure
- No separate storage costs
- Limited by Telegram's limits
- Requires Telegram account

## Future Features

### Will there be a mobile app?

Planned for future. The web interface works on mobile browsers for now.

### Will there be user authentication?

Yes, planned for multi-user support.

### Will there be thumbnail previews?

Yes, planned feature.

### Can I upload files to Telegram?

Not currently, but planned.

### Will there be torrent support?

Possible future feature to match Seedr functionality.

### Can I contribute?

Yes! Contributions welcome. Check the repository for guidelines.

## Legal & Compliance

### Is this legal?

Yes, it uses Telegram's official API. However, you must comply with:
- Telegram's Terms of Service
- Your country's laws
- Copyright laws

### Can I use it commercially?

The software is MIT licensed (free for commercial use), but:
- Respect Telegram's ToS
- Don't abuse the API
- Consider rate limits
- Respect copyright

### What about copyright?

You're responsible for the content you access. Don't:
- Share copyrighted content without permission
- Violate content creators' rights
- Use for piracy

## Support

### Where can I get help?

1. Read the documentation
2. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. Search GitHub issues
4. Open a new issue

### How do I report bugs?

Open a GitHub issue with:
- Description of the problem
- Steps to reproduce
- Error messages/logs
- System information

### How do I request features?

Open a GitHub issue with:
- Feature description
- Use case
- Why it's useful

### Can I hire someone to set this up?

This is open source software. You can hire any developer familiar with Python/Docker to help you set it up.

## Miscellaneous

### Why did you build this?

To provide a self-hosted alternative to cloud storage services, leveraging Telegram's excellent infrastructure.

### Is there a hosted version?

No, it's designed to be self-hosted for privacy and control.

### Can I white-label it?

Yes, MIT license allows this. Just keep the license notice.

### How can I support the project?

- Star the repository
- Report bugs
- Contribute code
- Share with others
- Write documentation

### What's the roadmap?

Check the GitHub repository for planned features and milestones.
