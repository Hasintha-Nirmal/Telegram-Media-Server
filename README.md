# Telegram Media Server

> Transform your Telegram account into a personal cloud storage system with a Seedr-style web interface

A self-hosted media server that indexes all media from your Telegram chats and provides a modern web interface for browsing, searching, streaming, and downloading. Think of it as your personal Netflix/Seedr powered by Telegram.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)

## 📚 Documentation

All documentation has been moved to the [docs/](docs/) folder for better organization.

**Quick Links:**
- 📖 [Documentation Index](docs/README.md) - Complete documentation overview
- 🚀 [Quick Start Guide](docs/QUICKSTART.md) - Get started in 5 minutes
- ⚙️ [Setup Instructions](docs/SETUP.md) - Detailed setup guide
- 🔧 [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions
- 🔐 [Session Management](docs/SESSION_MANAGEMENT.md) - Multi-account guide
- 📡 [API Documentation](docs/API.md) - REST API reference
- ❓ [FAQ](docs/FAQ.md) - Frequently asked questions

See [DOCS.md](DOCS.md) for a complete quick reference guide.

## ✨ Key Features

### Core Features
- � **Session-based authentication** - No password required, uses existing Telegram session
- 👥 **Multi-account support** - Create, upload, and switch between multiple Telegram accounts in the web UI
- 🔒 **Privacy isolation** - Each account has its own separate database
- 🔍 **Automatic discovery** - Scans all your chats (channels, groups, private chats, bots)
- 🎥 **Video streaming** - Stream videos directly in browser with seeking support
- 🔍 **Powerful search** - Search by filename, chat, type, size, and date
- 📥 **Smart downloads** - Queue-based system with parallel downloads
- 🔄 **Auto-sync** - Automatically indexes new media every 10 minutes
- 🐳 **Docker-first** - Production-ready containerized deployment
- 📊 **Modern dashboard** - Clean web interface with statistics

### Media Support
- Videos (MP4, MKV, AVI, MOV, WebM)
- Photos (JPG, PNG, GIF, WebP)
- Audio (MP3, WAV, OGG, FLAC)
- Documents (PDF, DOC, ZIP, etc.)
- Voice messages
- GIFs

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone <repository-url>
cd telegram-media-server

# 2. Get Telegram API credentials from https://my.telegram.org

# 3. Create .env file
cp .env.example .env
# Edit .env and add your API_ID and API_HASH

# 4. Create session file
python scripts/create_session.py

# 5. Start the server
docker-compose up

# 6. Open http://localhost:8080
```

For detailed instructions, see [docs/QUICKSTART.md](docs/QUICKSTART.md)

## 🎯 Use Cases

- **Personal Cloud Storage** - Use Telegram as unlimited cloud storage
- **Media Library** - Organize and stream your media collection
- **Content Archival** - Archive important media from channels/groups
- **Multi-Account Management** - Manage multiple Telegram accounts
- **Family Sharing** - Share media server with family members

## 🔒 Privacy & Security

- **Per-Account Isolation** - Each account has its own database
- **No Data Sharing** - Complete privacy between accounts
- **Local Storage** - All data stays on your server
- **Session-Based Auth** - No passwords stored
- **Docker Isolation** - Containerized for security

## 🛠️ Technology Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy
- **Database**: SQLite (default) or PostgreSQL
- **Telegram**: Telethon library
- **Frontend**: HTML5, Vanilla JavaScript
- **Deployment**: Docker, Docker Compose

## 📖 Documentation Structure

```
docs/
├── README.md                      # Documentation index
├── QUICKSTART.md                  # Quick start guide
├── SETUP.md                       # Detailed setup
├── API.md                         # API documentation
├── FEATURES.md                    # Feature list
├── ARCHITECTURE.md                # System architecture
├── SESSION_MANAGEMENT.md          # Multi-account guide
├── SESSION_TROUBLESHOOTING.md     # Session issues
├── TROUBLESHOOTING.md             # General troubleshooting
├── FAQ.md                         # FAQ
├── PRIVACY_FIX.md                 # Privacy isolation details
└── REBUILD.md                     # Rebuild instructions
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- [Telethon](https://github.com/LonamiWebs/Telethon) - Telegram client library
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM

## 📞 Support

- Check [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common issues
- Check [docs/FAQ.md](docs/FAQ.md) for frequently asked questions
- Open an issue for bugs or feature requests

---

Made with ❤️ for the Telegram community
```bash
pip install telethon
python -c "
from telethon import TelegramClient
client = TelegramClient('account', YOUR_API_ID, 'YOUR_API_HASH')
client.start()
print('Session created!')
"
```

### 3. Setup and Run
```bash
# Clone repository
git clone <repository-url>
cd telegram-media-server

# Create data directory
mkdir -p data/session
mv account.session data/session/

# Configure environment
cp .env.example .env
# Edit .env with your API_ID and API_HASH

# Start server
docker-compose up -d

# Access web interface
open http://localhost:8080
```

### 4. Index Your Media
1. Click "🔍 Scan Chats" to discover all chats
2. Click "📥 Scan All Media" to index media (may take a few minutes)
3. Start browsing, searching, and streaming!

## 📖 Documentation

- **[Documentation Index](DOCUMENTATION_INDEX.md)** - Complete documentation guide
- **[Quick Start Guide](QUICKSTART.md)** - Get running in 5 minutes
- **[Setup Guide](SETUP.md)** - Detailed installation and configuration
- **[FAQ](FAQ.md)** - Frequently asked questions
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions
- **[API Documentation](API.md)** - Complete API reference
- **[Architecture](ARCHITECTURE.md)** - System design and internals
- **[Features](FEATURES.md)** - Complete feature list
- **[Project Structure](PROJECT_STRUCTURE.md)** - Code organization

## 🎯 Use Cases

- **Personal Media Library**: Browse all your Telegram media in one place
- **Video Streaming**: Stream videos without downloading
- **Media Backup**: Download important files for safekeeping
- **Content Organization**: Automatically organize media by chat
- **Search & Discovery**: Find that video you saved months ago
- **API Integration**: Build custom tools on top of the API

## 🏗️ Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP/REST
┌──────▼──────────────────────┐
│   FastAPI Web Server        │
│  ┌────────┐  ┌────────┐    │
│  │Scanner │  │Streamer│    │
│  └────────┘  └────────┘    │
└──────┬──────────────────────┘
       │
┌──────▼──────┐    ┌──────────┐
│  Database   │    │ Telegram │
│ (SQLite/PG) │    │  Servers │
└─────────────┘    └──────────┘
```

## 🛠️ Technology Stack

- **Backend**: Python 3.11, FastAPI, Telethon
- **Database**: SQLite (default) or PostgreSQL
- **Frontend**: HTML5, JavaScript (vanilla)
- **Deployment**: Docker, Docker Compose
- **API**: RESTful with JSON

## 📊 Statistics Example

After indexing, you'll see:
- Total chats: 150+
- Total media: 10,000+
- Storage: 50GB+
- Media types: Videos, photos, documents, audio

## 🔒 Security & Privacy

- **Self-hosted**: All data stays on your server
- **No third parties**: Direct connection to Telegram
- **Session security**: Session file provides full account access - keep it secure
- **No authentication**: Current version has no auth - add reverse proxy for production

## 🚢 Deployment Options

### Docker (Recommended)
```bash
docker-compose up -d
```

### Docker with PostgreSQL
```bash
docker-compose -f docker-compose.postgres.yml up -d
```

### Local Development
```bash
pip install -r requirements.txt
python main.py
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Frontend framework (React/Vue)
- User authentication
- Thumbnail generation
- Advanced search
- Mobile app

## 📝 License

MIT License - feel free to use for personal or commercial projects

## ⚠️ Disclaimer

This tool uses your Telegram account. Use responsibly and comply with Telegram's Terms of Service. The developers are not responsible for any misuse or account restrictions.

## 🙏 Acknowledgments

- [Telethon](https://github.com/LonamiWebs/Telethon) - Telegram client library
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database toolkit

## 📞 Support

- **Issues**: Open an issue on GitHub
- **Documentation**: Check the docs folder
- **Questions**: See SETUP.md for troubleshooting

---

**Star ⭐ this repo if you find it useful!**
