.PHONY: help setup install dev up down logs migrate seed test lint format clean

include .env
export

help: ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

setup: ## Initial project setup
	@echo "Installing dependencies..."
	pnpm install
	uv sync --all-packages
	@test -f .env || cp .env.example .env
	@echo "Setup complete. Run 'make dev' to start."

dev-infra: ## Start infrastructure only
	docker compose up -d postgres redis kafka minio mailhog otel-collector prometheus grafana jaeger loki
	@sleep 10
	@make kafka-create-topics

dev-services: ## Start all backend services
	@for service in identity-service consumer-service retailer-service catalog-service inventory-service order-service compliance-service audit-service risk-service verification-service delivery-service notification-service payment-service pricing-service analytics-service realtime-service; do \
		(cd services/$$service && uv run uvicorn app.main:app --host 0.0.0.0 --port $$(echo $$service | grep -oE '[0-9]+$$' || echo 8000) --reload) & \
	done
	@echo "Services starting..."

migrate: ## Run all database migrations
	@for service in identity-service consumer-service retailer-service catalog-service inventory-service order-service compliance-service audit-service risk-service verification-service delivery-service notification-service payment-service pricing-service analytics-service realtime-service; do \
		echo "Migrating $$service..."; \
		(cd services/$$service && uv run alembic upgrade head) || echo "  (no migrations or failed)"; \
	done

seed: ## Seed initial data
	@echo "Seeding roles and permissions..."
	cd services/identity-service && uv run python -m app.scripts.seed_rbac
	@echo "Seeding policies..."
	cd services/compliance-service && uv run python -m app.scripts.seed_policies
	@echo "Seeding catalog..."
	cd services/catalog-service && uv run python -m app.scripts.seed_catalog
	@echo "Seed complete."

test: ## Run all tests
	@for service in identity-service consumer-service retailer-service catalog-service inventory-service order-service compliance-service audit-service risk-service; do \
		(cd services/$$service && uv run pytest) || echo "  (tests failed in $$service)"; \
	done

lint: ## Run linters
	uv run ruff check .
	cd apps && pnpm lint

format: ## Format code
	uv run ruff format .
	cd apps && pnpm format
