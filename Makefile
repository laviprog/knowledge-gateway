.DEFAULT_GOAL := help

.PHONY: help compose-config build up down logs ps check format

help:
	@echo "Available targets:"
	@echo "  compose-config  Validate docker compose config"
	@echo "  build           Build docker images"
	@echo "  up              Start services in background"
	@echo "  down            Stop services"
	@echo "  logs            Follow container logs"
	@echo "  ps              Show running containers"
	@echo "  check           Run linters and type checks"
	@echo "  format          Auto-format code"

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

check:
	uv run ruff check && \
	uv run ruff format --check && \
	uv run ty check

format:
	uv run ruff check --fix && \
	uv run ruff format
