.PHONY: help up down logs build dev test lint format typecheck migrate shell-backend shell-db clean status health test-backend test-frontend lint-backend lint-frontend

help:         ## Show available commands
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

up:           ## Start all services with docker compose
	@docker compose up -d

down:         ## Stop all services
	@docker compose down

logs:         ## Tail logs from all services
	@docker compose logs -f

build:        ## Build all Docker images
	@docker compose build

dev:          ## Start in development mode
	@docker compose up --build

test: test-backend test-frontend ## Run all tests (backend + frontend)

test-backend: ## Run backend tests
	@cd backend && pytest tests/

test-frontend:## Run frontend tests
	@cd frontend && npm run test

lint: lint-backend lint-frontend ## Run all linters

lint-backend: ## Run ruff + mypy
	@cd backend && ruff check . && mypy app/

lint-frontend:## Run eslint + tsc
	@cd frontend && npm run lint

format:       ## Format all code
	@cd backend && ruff format .
	@cd frontend && npm run format

typecheck:    ## Run type checkers
	@cd backend && mypy app/
	@cd frontend && npm run typecheck

migrate:      ## Run database migrations
	@cd backend && alembic upgrade head

migrate-create: ## Create new migration (usage: make migrate-create NAME=description)
	@cd backend && alembic revision --autogenerate -m "$(NAME)"

seed:         ## Run the database seed script
	@cd backend && python scripts/seed.py

shell-backend:## Open shell in backend container
	@docker compose exec backend bash

shell-db:     ## Open psql shell
	@docker compose exec postgres psql -U itr_user -d incident_regression_db

clean:        ## Remove containers, volumes, build artifacts
	@docker compose down -v
	@rm -rf backend/.pytest_cache backend/.mypy_cache backend/.ruff_cache backend/__pycache__
	@rm -rf frontend/dist frontend/node_modules

status:       ## Show service status
	@docker compose ps

health:       ## Check health endpoints
	@echo "Checking API health..."
	@curl -s http://localhost:8000/api/v1/health || echo "API is down"
	@echo "\nChecking Database health..."
	@curl -s http://localhost:8000/api/v1/health/database || echo "DB check failed"
	@echo ""
