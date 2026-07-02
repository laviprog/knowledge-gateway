<div align="center">

# Knowledge Gateway

> A private LLM gateway with retrieval-augmented generation. OpenAI-compatible API, vector search
> over your documents, and per-user rate limiting — all self-hosted.

[![Tests](https://github.com/laviprog/knowledge-gateway/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/laviprog/knowledge-gateway/actions/workflows/tests.yml)
[![Linting](https://github.com/laviprog/knowledge-gateway/actions/workflows/lint.yml/badge.svg?branch=main)](https://github.com/laviprog/knowledge-gateway/actions/workflows/lint.yml)
[![Type Checking](https://github.com/laviprog/knowledge-gateway/actions/workflows/typecheck.yml/badge.svg?branch=main)](https://github.com/laviprog/knowledge-gateway/actions/workflows/typecheck.yml)
[![Admin](https://github.com/laviprog/knowledge-gateway/actions/workflows/admin.yml/badge.svg?branch=main)](https://github.com/laviprog/knowledge-gateway/actions/workflows/admin.yml)
[![Coverage](https://raw.githubusercontent.com/laviprog/knowledge-gateway/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/laviprog/knowledge-gateway/blob/python-coverage-comment-action-data/htmlcov/index.html)

![License](https://img.shields.io/badge/License-MIT-green)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.130+-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?logo=postgresql&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-1.17+-FF4500?logo=qdrant&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7+-DC382D?logo=redis&logoColor=white)
![OpenAI SDK](https://img.shields.io/badge/OpenAI_SDK-compatible-412991?logo=openai&logoColor=white)

</div>

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
- [Development](#development)
- [Testing](#testing)
- [API Overview](#api-overview)
- [License](#license)

## Features

- **OpenAI-compatible API** — `POST /chat/completions` with streaming and `GET /models`.
- **RAG pipeline** — documents are chunked, embedded, and stored in Qdrant; matching chunks are
  injected into the chat prompt at request time.
- **Per-user rate limiting** — sliding-window rate limiter backed by Redis; configurable per user,
  with `0` meaning unlimited (admin accounts are unlimited by default).
- **API key authentication** — keys are stored as HMAC-SHA256 hashes with a server-side pepper;
  the raw key is returned only once at creation.
- **Admin API** — manage users, API keys, documents, and LLM model records through dedicated
  endpoints (hidden from public docs in production).
- **Admin panel** — a React + Refine + shadcn/ui web UI for the admin API: CRUD for every resource,
  API key issuing, document upload, knowledge-base search, request logs, and usage analytics. See
  [`admin/README.md`](admin/README.md).
- **Chat usage logging** — every request records user, model, status, token counts, latency, and
  errors.
- **Multi-format document ingestion** — plain text, PDF, and DOCX via MarkItDown; chunks are
  indexed asynchronously.
- **Structured logging** — JSON log output with per-request correlation IDs and trusted-proxy IP
  resolution.
- **Alembic migrations** — schema changes are versioned and applied automatically on startup.
- **Docker Compose deployment** — all dependencies (Postgres, Qdrant, Redis) included.

## Getting Started

### Quick Start

```bash
# 1. Clone and configure
cp .env.example .env
# Edit .env — at minimum set: POSTGRES_PASSWORD, QDRANT_API_KEY, API_KEY_PEPPER, PROVIDER_SECRET_KEY, and BOOTSTRAP_ADMIN_API_KEY

# 2. Build and start all services
make build
make up

# 3. Verify everything is healthy
make ps
make logs
```

The API will be available at `http://127.0.0.1:8080/api/v1`.  
Interactive API docs (Scalar) at `http://127.0.0.1:8080/api/v1/docs` (requires `ENV=dev`).
The admin panel will be available at `http://127.0.0.1:8090/`

Docker Compose runs database migrations automatically before the API starts.

### First-time setup

The system ships with no inference configuration — an admin creates it via the admin API
(`ENV=dev` exposes these routes in the docs) in this order:

1. **Provider** (`POST /providers`) — base URL + (encrypted) API key of an OpenAI-compatible
   endpoint.
2. **Embedding model** (`POST /embedding-models`) — `provider_model` + provider; owns a Qdrant
   collection.
3. **Knowledge base** (`POST /knowledge-bases`) — bound to an embedding model; documents are
   uploaded into it and retrieved from it.
4. **LLM model** (`POST /llm-models`) — `provider_model` + provider; exposed via `GET /models`.

Clients pick a knowledge base per request by passing `knowledge_base_id` in the chat completion
body (OpenAI SDK `extra_body`); omitting it runs the completion without retrieval.

## Development

```bash
# Install all dependency groups (api, migrate, dev)
make setup

# Install Git hooks — ruff + ty on Python, Biome on the admin panel (run on commit)
make hooks

# Lint, type-check, and format
make check
make format

# Run tests
make test
```

Admin and dev-only routes are included in the OpenAPI schema only when `ENV=dev`.

The admin panel has its own toolchain (Node, Biome, Vitest); see [
`admin/README.md`](admin/README.md) for its development and deployment workflow.

## Testing

The test suite uses `pytest` with `anyio` for async tests and `httpx` for HTTP-level testing.

```bash
make test      # run all tests
make coverage  # run all tests with a coverage report
make check     # lint + format check + type check
```

CI runs the suite with coverage on every push and pull request; the
[`python-coverage-comment-action`](https://github.com/py-cov-action/python-coverage-comment-action)
posts a coverage summary on pull requests and refreshes the coverage badge above. The admin panel
has a separate CI job (Biome + `tsc` + Vitest + build) — see the **Admin** badge above and
[`admin/README.md`](admin/README.md).

## API Overview

All requests are authenticated with a bearer API key:

```http
Authorization: Bearer <api_key>
```

Keys are stored only as hashes — the raw key is returned once at creation time.

**User-facing endpoints:**

| Method | Path                | Description                                    |
|--------|---------------------|------------------------------------------------|
| `GET`  | `/models`           | List available OpenAI-compatible model IDs     |
| `POST` | `/chat/completions` | Create a chat completion (streaming supported) |

The `/chat/completions` endpoint enforces a per-user sliding-window rate limit. The limit is
configured per user record and defaults to `RATE_LIMIT_DEFAULT_REQUESTS_PER_MINUTE`. Admin accounts
are always unlimited.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
