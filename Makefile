# ==============================================================================
# The Churninator - Project Makefile (v2.2 - Final)
# ==============================================================================
# This Makefile is the central control panel for all development and
# operational tasks for the Churninator platform.
#
# It is environment-aware:
#   - `make up` (default): uses `docker-compose.yml` for local dev.
#   - `make up ENV=prod`: uses `docker-compose.prod.yml` for production.
# ==============================================================================

# Use bash for more advanced shell features like `read -p`.
SHELL := /bin/bash

# Load environment variables from .env file. Suppress errors if it doesn't exist.
-include .env

# --- Environment-Aware Docker Compose Configuration ---
# Default to the local development compose file.
COMPOSE_FILE := docker-compose.yml

# If the ENV variable is set to "prod", use the production compose file.
ifeq ($(ENV), prod)
    COMPOSE_FILE := docker-compose.prod.yml
endif

# Define the base command for all docker-compose actions
DOCKER_COMPOSE_COMMAND := docker-compose -f $(COMPOSE_FILE)

# --- Project-Wide Operations ---
.PHONY: help up down logs prune clean

help: ## ✨ Show this help message
	@echo "Usage: make [target] [ENV=prod]"
	@echo ""
	@echo "The Churninator Project Control"
	@echo "--------------------------------"
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## 🚀 Build and start services. Use 'make up ENV=prod' for production.
	@echo "🚀 Starting services using configuration: $(COMPOSE_FILE)"
	@$(DOCKER_COMPOSE_COMMAND) up --build -d

down: ## 🛑 Stop services. Use 'make down ENV=prod' for production.
	@echo "🛑 Stopping services using configuration: $(COMPOSE_FILE)"
	@$(DOCKER_COMPOSE_COMMAND) down

logs: ## 📜 Follow logs. Use 'make logs ENV=prod' for production.
	@echo "📜 Tailing logs... (Press Ctrl+C to exit)"
	@$(DOCKER_COMPOSE_COMMAND) logs -f

prune: down ## 🧹 Stop services and remove all Docker data (DANGEROUS).
	@echo "🧹 Pruning all Docker data for a clean slate..."
	@$(DOCKER_COMPOSE_COMMAND) down -v --rmi all
	@echo "✅ System pruned."

clean: ## 🧼 Remove Python and Next.js build artifacts from the local filesystem.
	@echo "🧼 Cleaning project artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	@echo "✅ Project cleaned."

# --- Service-Specific Targets ---
.PHONY: api-logs api-shell worker-logs worker-shell inference-logs inference-shell frontend-logs frontend-shell

api-logs: ## 📜 Follow logs for the backend API service only.
	@$(DOCKER_COMPOSE_COMMAND) logs -f api

api-shell: ## 💻 Open a bash shell inside the running backend API container.
	@$(DOCKER_COMPOSE_COMMAND) exec api bash

worker-logs: ## 📜 Follow logs for the Dramatiq worker service only.
	@$(DOCKER_COMPOSE_COMMAND) logs -f worker

worker-shell: ## 💻 Open a bash shell inside the running worker container.
	@$(DOCKER_COMPOSE_COMMAND) exec worker bash

inference-logs: ## 📜 Follow logs for the ML inference service only.
	@$(DOCKER_COMPOSE_COMMAND) logs -f inference_server

inference-shell: ## 💻 Open a bash shell inside the running inference container.
	@$(DOCKER_COMPOSE_COMMAND) exec inference_server bash

frontend-logs: ## 📜 Follow logs for the Next.js frontend service only.
	@$(DOCKER_COMPOSE_COMMAND) logs -f frontend

frontend-shell: ## 💻 Open a bash shell inside the running frontend container.
	@$(DOCKER_COMPOSE_COMMAND) exec frontend bash

# --- Database & Alembic Migrations ---
.PHONY: db-migrate db-upgrade db-downgrade db-shell


ALEMBIC_CMD = alembic -c backend/alembic.ini

db-migrate: ## 🐘 Generate a new Alembic database migration file.
	@echo "🐘 Generating new Alembic migration..."
	@read -p "Enter a short, descriptive message for the migration (e.g., add_new_field_to_users): " msg; \
	$(DOCKER_COMPOSE_COMMAND) run --rm api $(ALEMBIC_CMD) revision --autogenerate -m "$$msg"
	@echo "✅ New migration file created in backend/src/db/migrations/versions/"

db-upgrade: ## 🚀 Apply all pending database migrations to the 'head'.
	@echo "🚀 Applying database migrations..."
	@$(DOCKER_COMPOSE_COMMAND) run --rm api $(ALEMBIC_CMD) upgrade head
	@echo "✅ Database is up to date."

db-downgrade: ## ↩️ Downgrade the database by one revision.
	@echo "↩️ Downgrading database by one revision..."
	@$(DOCKER_COMPOSE_COMMAND) run --rm api $(ALEMBIC_CMD) downgrade -1
	@echo "✅ Database downgraded."

db-shell: ## 📦 Open a psql shell to the running database.
	@$(DOCKER_COMPOSE_COMMAND) exec db psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)
