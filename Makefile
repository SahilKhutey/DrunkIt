.PHONY: help setup dev infra down migrate seed psql test lint typecheck

help:
	@echo "FACCP Monorepo Commands:"
	@echo "  make setup     - Install Python common package and pnpm dependencies"
	@echo "  make infra     - Start PostgreSQL, Redis, Kafka, MinIO, MailHog"
	@echo "  make down      - Stop all infrastructure containers"
	@echo "  make dev       - Run Next.js web applications in dev mode"
	@echo "  make migrate   - Run Alembic migrations for identity service"
	@echo "  make seed      - Seed RBAC roles and permissions"
	@echo "  make test      - Run pytest across Python microservices"
	@echo "  make typecheck - Run TypeScript typechecks across apps and packages"

setup:
	pip install -e services/_common
	pnpm install

infra:
	docker compose up -d postgres redis zookeeper kafka minio mailhog otel-collector prometheus grafana jaeger

down:
	docker compose down

dev:
	pnpm dev

migrate:
	cd services/identity-service && alembic upgrade head

seed:
	python -m identity_app.scripts.seed_rbac

test:
	pytest tests/unit/

typecheck:
	pnpm typecheck
