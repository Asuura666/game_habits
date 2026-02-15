# HabitQuest Makefile
# Quick commands for development and deployment

.PHONY: help up down restart logs seed test lint migrate

# Default target
help:
	@echo "HabitQuest Commands:"
	@echo "  make up        - Start all services"
	@echo "  make down      - Stop all services"
	@echo "  make restart   - Restart all services"
	@echo "  make logs      - Tail all logs"
	@echo "  make seed      - Seed database (badges, items)"
	@echo "  make test      - Run backend tests"
	@echo "  make lint      - Run linters"
	@echo "  make migrate   - Run database migrations"
	@echo "  make shell     - Open backend shell"

# Docker commands
up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

# Database
migrate:
	docker compose exec backend alembic upgrade head

seed: seed-items seed-badges
	@echo "✅ Database seeded!"

seed-items:
	@echo "🛒 Seeding shop items..."
	docker compose exec backend python scripts/seed_items.py

seed-badges:
	@echo "🏆 Seeding badges..."
	docker compose exec backend python scripts/seed_badges.py

# Development
test:
	docker compose exec backend pytest -v

lint:
	docker compose exec backend ruff check app/
	docker compose exec backend mypy app/

shell:
	docker compose exec backend python

# Full setup for fresh deployment
setup: up migrate seed
	@echo "🎮 HabitQuest ready!"
