.PHONY: help build up down logs restart clean session

help:
	@echo "Telegram Media Server - Make Commands"
	@echo ""
	@echo "  make build      - Build Docker image"
	@echo "  make up         - Start server"
	@echo "  make down       - Stop server"
	@echo "  make logs       - View logs"
	@echo "  make restart    - Restart server"
	@echo "  make clean      - Remove containers and volumes"
	@echo "  make session    - Create Telegram session"
	@echo "  make postgres   - Start with PostgreSQL"
	@echo ""

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Server started at http://localhost:8080"

down:
	docker-compose down

logs:
	docker-compose logs -f

restart:
	docker-compose restart

clean:
	docker-compose down -v
	@echo "Cleaned up containers and volumes"

session:
	python scripts/create_session.py

postgres:
	docker-compose -f docker-compose.postgres.yml up -d
	@echo "Server with PostgreSQL started at http://localhost:8080"
