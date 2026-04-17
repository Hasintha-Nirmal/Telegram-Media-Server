<div align="center">

# 📡 Telegram Media Server

**Self-hosted media streaming & management server powered by Telegram**

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)](https://docker.com)
[![Pyrogram](https://img.shields.io/badge/Pyrogram-MTProto-green)](https://pyrogram.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Stars](https://img.shields.io/github/stars/Hasintha-Nirmal/Telegram-base-app?style=social)](https://github.com/Hasintha-Nirmal/Telegram-base-app)

> Stream, browse, and manage all your Telegram media through a sleek web interface — fully self-hosted, privacy-first.

[🚀 Quick Start](#quick-start) · [📖 Docs](docs/README.md) · [🐛 Issues](../../issues) · [⭐ Star this repo](#)

</div>

---

## ✨ Features

- 📁 **Browse & stream** media from any Telegram channel or chat
- 🌐 **Modern Web UI** — clean, responsive interface
- 🐳 **Docker ready** — one command to run everything
- 🗄️ **PostgreSQL** — reliable media metadata storage
- 🔐 **Session management** — secure Pyrogram session handling
- ⚡ **Fast streaming** — direct media delivery
- 🔧 **Fully configurable** via `.env`

---

## 🚀 Quick Start

**1. Clone the repo**
```bash
git clone https://github.com/Hasintha-Nirmal/Telegram-Media-Server.git
cd Telegram-Media-Server
```

**2. Copy environment file**
```bash
cp .env.example .env
```

**3. Add your Telegram API credentials to `.env`**

**4. Start everything**
```bash
docker-compose up -d
```

Open `http://localhost:8000` in your browser. That's it! 🎉

---

## 📋 Requirements

- Docker & Docker Compose
- Telegram API credentials ([get them here](https://my.telegram.org))
- Python 3.10+ (if running without Docker)

---

## 🏗️ Project Structure

```
telegram-media-server/
├── app/           # Core application logic
├── data/          # Media & data storage
├── database/      # PostgreSQL models & migrations
├── docs/          # Full documentation
├── scripts/       # Utility scripts
├── web/           # Web UI (HTML/CSS/JS)
├── main.py        # Entry point
└── docker-compose.yml
```

---

## 📖 Documentation

| Guide | Description |
|-------|-------------|
| [Quick Start](docs/QUICKSTART.md) | Get running in 5 minutes |
| [API Reference](docs/API.md) | REST API endpoints |
| [Architecture](docs/ARCHITECTURE.md) | System design |
| [Session Management](docs/SESSION_MANAGEMENT.md) | Pyrogram sessions |
| [Troubleshooting](docs/FAQ.md) | Common issues & fixes |

---

## 🤝 Contributing

PRs are welcome! Check out the [docs](docs/README.md) to understand the architecture before contributing.

---

## ⭐ Support

If this project helped you, please **star the repo** — it helps others find it!

---

<div align="center">
Made with ❤️ by <a href="https://github.com/Hasintha-Nirmal">Hasintha Nirmal</a> · 🇱🇰 Sri Lanka
</div>
