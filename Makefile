.DEFAULT_GOAL := help

.PHONY: help setup hooks compose-config build up down logs ps migrate migration-heads test check format

help:
	@echo "Available targets:"
	@echo "  setup           Install project dependencies"
	@echo "  hooks           Install Git hooks"
	@echo "  compose-config  Validate docker compose config"
	@echo "  build           Build docker images"
	@echo "  up              Start services in background"
	@echo "  down            Stop services"
	@echo "  logs            Follow container logs"
	@echo "  ps              Show running containers"
	@echo "  migrate         Apply database migrations"
	@echo "  migration-heads Show Alembic migration heads"
	@echo "  test            Run test suite"
	@echo "  check           Run linters and type checks"
	@echo "  format          Auto-format code"

setup:
	uv sync --all-groups

hooks:
	uv run pre-commit install

compose-config:
	docker compose config --quiet

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps

migrate:
	uv run alembic upgrade head

migration-heads:
	uv run alembic heads

test:
	uv run pytest -v

check:
	uv run ruff check && \
	uv run ruff format --check && \
	uv run ty check

format:
	uv run ruff check --fix && \
	uv run ruff format
