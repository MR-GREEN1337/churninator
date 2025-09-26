# ==============================================================================
# The Churninator - Project Makefile
# ==============================================================================
# This Makefile is the central control panel for all development and
# operational tasks.
#
# Targets are organized by service: `backend`, `worker`, `inference`,
# `frontend`, `db` (for Alembic), and `project`.
#
# Common Commands:
#   make up        - Start all services for local development.
#   make down      - Stop and remove all services.
#   make logs      - View logs from all running services.
#   make db-migrate - Create a new database migration.
#   make db-upgrade - Apply pending database migrations.
# ==============================================================================

# Use bash for more advanced shell features
SHELL := /bin/bash

# Load environment variables from .env file for use in this Makefile
include .env

# --- Project-Wide Operations ---

.PHONY: help up down logs prune clean

help: ## ✨ Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## 🚀 Start all services in detached mode using Docker Compose
	@echo "🚀 Starting all Churninator services..."
	docker-compose up --build -d

down: ## 🛑 Stop and remove all running services
	@echo "🛑 Stopping all Churninator services..."
	docker-compose down

logs: ## 📜 Follow logs from all services
	@echo "📜 Tailing logs for all services... (Press Ctrl+C to exit)"
	docker-compose logs -f

prune: down ## 🧹 Stop services and remove all Docker volumes, networks, and images (DANGEROUS)
	@echo "🧹 Pruning all Docker data for a clean slate..."
	docker-compose down -v --rmi all
	@echo "✅ System pruned."

clean: ## 🧼 Remove Python and Next.js build artifacts
	@echo "🧼 Cleaning project artifacts..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	@echo "✅ Project cleaned."


# --- Backend API Service ---

.PHONY: backend-logs backend-shell backend

backend:
	@echo "🚀 Running the backend API service..."
	cd backend && uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000

backend-logs: ## 📜 Follow logs for the backend API service only
	docker-compose logs -f api

backend-shell: ## 💻 Open a bash shell inside the running backend API container
	docker-compose exec api bash


# --- Worker Service ---

.PHONY: worker-logs worker-shell worker

worker:
	@echo "🚀 Running the Dramatiq worker service..."
	cd worker && uv run dramatiq run

worker-logs: ## 📜 Follow logs for the Dramatiq worker service only
	docker-compose logs -f worker

worker-shell: ## 💻 Open a bash shell inside the running worker container
	docker-compose exec worker bash


# --- Inference Service ---

.PHONY: inference-logs inference-shell inference

inference:
	@echo "🚀 Running the ML inference service..."
	cd inference && uv run python inference.py

inference-logs: ## 📜 Follow logs for the ML inference service only
	docker-compose logs -f inference

inference-shell: ## 💻 Open a bash shell inside the running inference container
	docker-compose exec inference bash


# --- Frontend (Web) Service ---

.PHONY: frontend-logs frontend-shell frontend

frontend:
	@echo "🚀 Running the Next.js frontend service..."
	cd web && npm run dev

frontend-logs: ## 📜 Follow logs for the Next.js frontend service only
	docker-compose logs -f web # Assuming your frontend service is named 'web' in docker-compose.yml

frontend-shell: ## 💻 Open a bash shell inside the running frontend container
	docker-compose exec web bash


# --- Database & Alembic Migrations ---

.PHONY: db-migrate db-upgrade db-downgrade db-shell

db-migrate: ## 🐘 Generate a new Alembic database migration file
	@echo "🐘 Generating new Alembic migration..."
	@read -p "Enter a short, descriptive message for the migration: " msg; \
	docker-compose run --rm api alembic revision --autogenerate -m "$$msg"
	@echo "✅ New migration file created in backend/src/db/migrations/versions/"

db-upgrade: ## 🚀 Apply all pending database migrations to the 'head'
	@echo "🚀 Applying database migrations..."
	docker-compose run --rm api alembic upgrade head
	@echo "✅ Database is up to date."

db-downgrade: ## ↩️ Downgrade the database by one revision
	@echo "↩️ Downgrading database by one revision..."
	docker-compose run --rm api alembic downgrade -1
	@echo "✅ Database downgraded."

db-shell: ## 📦 Open a psql shell to the running database
	docker-compose exec db psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)
