# RAG Service

> A private LLM gateway with retrieval-augmented generation. OpenAI-compatible API, vector search
> over your documents, and per-request usage logging — all self-hosted.

[![Tests](https://github.com/laviprog/rag-service/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/laviprog/rag-service/actions/workflows/tests.yml)
[![Linting](https://github.com/laviprog/rag-service/actions/workflows/lint.yml/badge.svg?branch=main)](https://github.com/laviprog/rag-service/actions/workflows/lint.yml)
[![Type Checking](https://github.com/laviprog/rag-service/actions/workflows/typecheck.yml/badge.svg?branch=main)](https://github.com/laviprog/rag-service/actions/workflows/typecheck.yml)

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.130+-009688?logo=fastapi&logoColor=white)
![ty](https://custom-icon-badges.demolab.com/badge/ty-261230.svg?logo=ty-astral-logo)
![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?logo=postgresql&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-latest-FF4500?logo=qdrant&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-latest-000000?logo=ollama&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Development](#development)
- [Testing](#testing)
- [API Overview](#api-overview)
- [Roadmap](#roadmap)
- [License](#license)

## Features

- OpenAI-compatible `POST /chat/completions` endpoint with streaming support.
- OpenAI-compatible `GET /models` endpoint.
- API key authentication with hashed key storage.
- Admin-managed users, API keys, documents, and LLM model records.
- Global RAG knowledge base backed by Qdrant vector search.
- Document ingestion with chunking and background indexing.
- Ollama integration for embeddings and chat generation.
- Chat request usage logging by user, model, status, tokens, and latency.
- Alembic-managed PostgreSQL schema migrations.
- Docker Compose local deployment.

## Architecture

The service has three main responsibilities:

- **API gateway** — authenticates requests, exposes OpenAI-compatible chat and model endpoints, and
  provides admin endpoints.
- **Retrieval pipeline** — stores documents in PostgreSQL, indexes chunks in Qdrant, and injects
  matching chunks into chat prompts.
- **Usage accounting** — records chat completion request metadata, token counts, timings, and
  errors.

![Architecture Diagram](/assets/architecture.png)

Core storage:

- **PostgreSQL** — users, API keys, model records, documents, chunks, and usage logs.
- **Qdrant** — vector points for document chunks.
- **Ollama** — embedding and chat model inference.

## Getting Started

### Prerequisites

- Docker and Docker Compose
- `uv` for local development commands
- Ollama reachable from the API container via `OLLAMA_BASE_URL`
- Required Ollama models pulled locally:
    - embedding model configured by `OLLAMA_EMBEDDING_MODEL`
    - chat models referenced by records in `llm_models`

### Quick Start

```bash
# 1. Clone and configure
cp .env.example .env
# Edit .env — at minimum review POSTGRES_*, QDRANT_*, OLLAMA_*, and API_KEY_PEPPER

# 2. Build and start
make build
make up

# 3. Check everything is running
make ps
make logs
```

The API will be available at `http://127.0.0.1:8080/api/v1`.  
Interactive API docs (Scalar) at `http://127.0.0.1:8080/api/v1/docs`.

### Other Useful Commands

| Command                | Description                           |
|------------------------|---------------------------------------|
| `make compose-config`  | Validate Docker Compose configuration |
| `make down`            | Stop all services                     |
| `make migrate`         | Run database migrations manually      |
| `make migration-heads` | Show current migration heads          |

Docker Compose runs migrations automatically before the API starts.

## Configuration

Configuration is loaded from environment variables and `.env`.

| Variable                       | Description                                                                                      |
|--------------------------------|--------------------------------------------------------------------------------------------------|
| `ENV`                          | Environment mode; use `dev` to expose admin/dev routes in API docs                               |
| `ROOT_PATH`                    | API root path for deployments behind a reverse proxy                                             |
| `API_KEY_PEPPER`               | Secret pepper used when hashing API keys — set a stable value before creating keys in production |
| `BOOTSTRAP_ADMIN_NAME`         | Default admin username                                                                           |
| `BOOTSTRAP_ADMIN_API_KEY_NAME` | Default admin API key name                                                                       |
| `BOOTSTRAP_ADMIN_API_KEY`      | Optional fixed bootstrap admin API key                                                           |
| `POSTGRES_*`                   | PostgreSQL connection settings                                                                   |
| `QDRANT_*`                     | Qdrant connection settings                                                                       |
| `QDRANT_COLLECTION_NAME`       | Vector collection for document chunks                                                            |
| `OLLAMA_BASE_URL`              | Ollama service URL                                                                               |
| `OLLAMA_EMBEDDING_MODEL`       | Embedding model used for retrieval                                                               |
| `OLLAMA_TIMEOUT_SECONDS`       | Timeout for Ollama chat generation                                                               |
| `RAG_RETRIEVAL_LIMIT`          | Number of chunks retrieved per chat request                                                      |
| `RAG_CONTEXT_MAX_CHARS`        | Max retrieved context size injected into the prompt                                              |

## Development

Install dependencies:

```bash
make setup
```

Install Git hooks:

```bash
make hooks
```

Run static checks and auto-format:

```bash
make check
make format
```

Project layout:

- `src/rag_service` — application source code
- `migrations/versions` — Alembic migration files
- `bruno` — Bruno API request collections

Admin and dev routes are included in OpenAPI when `ENV=dev`.

## Testing

The project uses `pytest` for tests, `ruff` for linting and formatting, and `ty` for static type
checks.

```bash
make check
make test
```

## API Overview

Requests are authenticated with bearer API keys:

```http
Authorization: Bearer <api_key>
```

API keys are stored only as hashes — the raw key is returned once at creation time.

**Customer-facing endpoints:**

- `GET /models` — list available OpenAI-compatible model IDs.
- `POST /chat/completions` — create a chat completion, with optional streaming.

**Admin endpoints** manage:

- users and API keys
- LLM model records
- documents and document search
- chat completion usage logs

## Roadmap

- [ ] Add summary usage endpoint for aggregate request, token, latency, and error metrics.
- [ ] Add FastAPI endpoint tests for chat completions and admin usage listing.
- [ ] Add PostgreSQL integration tests for migrations, relationships, and soft delete behavior.
- [ ] Improve streaming interruption handling with explicit integration coverage.
- [ ] Add pricing tables or model cost configuration as the foundation for billing.
- [ ] Add optional retention and privacy controls for debug metadata.
- [ ] Document production deployment assumptions and operational runbooks.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
