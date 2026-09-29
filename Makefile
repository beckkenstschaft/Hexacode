# Makefile for Sahayak development

.PHONY: help setup dev test lint format migrate seed build docker-up docker-down clean

# Default target
help:
	@echo "Sahayak - Offline NPU-first meeting copilot"
	@echo ""
	@echo "Available targets:"
	@echo "  setup       - Install all dependencies (backend + frontend)"
	@echo "  dev         - Start development servers (backend + frontend)"
	@echo "  test        - Run all tests (backend + frontend)"
	@echo "  lint        - Run linters (backend + frontend)"
	@echo "  format      - Format code (backend + frontend)"
	@echo "  migrate     - Run database migrations"
	@echo "  seed        - Seed database with sample data"
	@echo "  build       - Build production images"
	@echo "  docker-up   - Start docker-compose (CPU only)"
	@echo "  docker-down - Stop docker-compose"
	@echo "  clean       - Clean build artifacts"

# Backend setup
backend-setup:
	cd backend && python -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"

# Frontend setup
frontend-setup:
	cd frontend && npm ci

# Full setup
setup: backend-setup frontend-setup
	@echo "Setup complete! Run 'make dev' to start development servers."

# Development servers
dev:
	@echo "Starting development servers..."
	@cd backend && . .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 & \
	cd frontend && npm run dev

# Backend only
dev-backend:
	cd backend && . .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend only
dev-frontend:
	cd frontend && npm run dev

# Tests
test: test-backend test-frontend

test-backend:
	cd backend && . .venv/bin/activate && pytest -v

test-frontend:
	cd frontend && npm run test

# Linting
lint: lint-backend lint-frontend

lint-backend:
	cd backend && . .venv/bin/activate && ruff check . && mypy app

lint-frontend:
	cd frontend && npm run lint

# Formatting
format: format-backend format-frontend

format-backend:
	cd backend && . .venv/bin/activate && ruff format .

format-frontend:
	cd frontend && npm run format

# Database migrations
migrate:
	cd backend && . .venv/bin/activate && alembic upgrade head

migrate-create:
	cd backend && . .venv/bin/activate && alembic revision --autogenerate -m "$(msg)"

# Seed data
seed:
	cd backend && . .venv/bin/activate && python scripts/seed_data.py

# Download models
download-models:
	cd backend && . .venv/bin/activate && python scripts/download_models.py

# Build
build: build-backend build-frontend

build-backend:
	cd backend && docker build -t sahayak-backend .

build-frontend:
	cd frontend && docker build -t sahayak-frontend .

# Docker
docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

# Clean
clean:
	rm -rf backend/.venv backend/__pycache__ backend/.pytest_cache backend/.mypy_cache backend/.ruff_cache
	rm -rf frontend/node_modules frontend/dist
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true

# Generate benchmark audio
benchmark-audio:
	cd backend && . .venv/bin/activate && python scripts/benchmark_audio.py