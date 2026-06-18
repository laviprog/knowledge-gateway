# RAG Service

> A private LLM gateway with retrieval-augmented generation. OpenAI-compatible API, vector search
> over your documents, and per-user rate limiting — all self-hosted.

[![Tests](https://github.com/laviprog/knowledge-gateway/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/laviprog/knowledge-gateway/actions/workflows/tests.yml)
[![Linting](https://github.com/laviprog/knowledge-gateway/actions/workflows/lint.yml/badge.svg?branch=main)](https://github.com/laviprog/knowledge-gateway/actions/workflows/lint.yml)
[![Type Checking](https://github.com/laviprog/knowledge-gateway/actions/workflows/typecheck.yml/badge.svg?branch=main)](https://github.com/laviprog/knowledge-gateway/actions/workflows/typecheck.yml)
[![Coverage](https://raw.githubusercontent.com/laviprog/knowledge-gateway/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/laviprog/knowledge-gateway/blob/python-coverage-comment-action-data/htmlcov/index.html)

![License](https://img.shields.io/badge/License-MIT-green)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.130+-009688?logo=fastapi&logoColor=white)
![ty](https://custom-icon-badges.demolab.com/badge/ty-261230.svg?logo=ty-astral-logo)
![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?logo=postgresql&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-1.17+-FF4500?logo=qdrant&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7+-DC382D?logo=redis&logoColor=white)
![OpenAI SDK](https://img.shields.io/badge/OpenAI_SDK-compatible-412991?logo=openai&logoColor=white)

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

- **OpenAI-compatible API** — `POST /chat/completions` with streaming and `GET /models`.
- **RAG pipeline** — documents are chunked, embedded, and stored in Qdrant; matching chunks are
  injected into the chat prompt at request time.
- **Per-user rate limiting** — sliding-window rate limiter backed by Redis; configurable per user,
  with `0` meaning unlimited (admin accounts are unlimited by default).
- **API key authentication** — keys are stored as HMAC-SHA256 hashes with a server-side pepper;
  the raw key is returned only once at creation.
- **Admin API** — manage users, API keys, documents, and LLM model records through dedicated
  endpoints (hidden from public docs in production).
- **Chat usage logging** — every request records user, model, status, token counts, latency, and
  errors.
- **Multi-format document ingestion** — plain text, PDF, and DOCX via MarkItDown; chunks are
  indexed asynchronously.
- **Structured logging** — JSON log output with per-request correlation IDs and trusted-proxy IP
  resolution.
- **Alembic migrations** — schema changes are versioned and applied automatically on startup.
- **Docker Compose deployment** — all dependencies (Postgres, Qdrant, Redis) included.

## Architecture

The service has three main responsibilities:

- **API gateway** — authenticates requests via hashed API keys, enforces per-user rate limits, and
  exposes OpenAI-compatible endpoints alongside admin routes.
- **Retrieval pipeline** — stores documents in PostgreSQL, indexes chunks in Qdrant, and injects
  matching context into chat prompts at request time.
- **Usage accounting** — records chat completion metadata: user, model, token counts, timings, and
  error codes.

![Architecture Diagram](/assets/architecture.png)

**Storage:**

| Store          | Purpose                                                           |
|----------------|-------------------------------------------------------------------|
| **PostgreSQL** | Users, API keys, model records, documents, chunks, and usage logs |
| **Qdrant**     | Vector points for document chunks (semantic search)               |
| **Redis**      | Sliding-window rate limit counters (per-user sorted sets)         |
| **LLM API**    | Embedding and chat model inference (any OpenAI-compatible API)    |

## Getting Started

### Prerequisites

- Docker and Docker Compose
- `uv` for local development
- An OpenAI-compatible API reachable at `LLM_BASE_URL` (OpenAI, Azure OpenAI, vLLM, Ollama's `/v1`,
  etc.) that serves:
    - the embedding model set by `LLM_EMBEDDING_MODEL`
    - any chat models you plan to register in `llm_models`

### Quick Start

```bash
# 1. Clone and configure
cp .env.example .env
# Edit .env — at minimum set: POSTGRES_PASSWORD, QDRANT_API_KEY, API_KEY_PEPPER,
#             BOOTSTRAP_ADMIN_API_KEY, LLM_BASE_URL, and LLM_EMBEDDING_MODEL

# 2. Build and start all services
make build
make up

# 3. Verify everything is healthy
make ps
make logs
```

The API will be available at `http://127.0.0.1:8080/api/v1`.  
Interactive API docs (Scalar) at `http://127.0.0.1:8080/api/v1/docs` (requires `ENV=dev`).

Docker Compose runs database migrations automatically before the API starts.

### Useful Commands

| Command                | Description                           |
|------------------------|---------------------------------------|
| `make up`              | Start all services in the background  |
| `make down`            | Stop all services                     |
| `make logs`            | Follow container logs                 |
| `make ps`              | Show running containers               |
| `make migrate`         | Run database migrations manually      |
| `make migration-heads` | Show current migration heads          |
| `make compose-config`  | Validate Docker Compose configuration |

## Configuration

All settings are loaded from environment variables or `.env`. See `.env.example` for a full
template with comments.

**Required:**

| Variable          | Description                                                                                                                       |
|-------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| `API_KEY_PEPPER`  | Secret used when hashing API keys — generate with `secrets.token_hex(32)` and never change it in production once keys are created |
| `POSTGRES_*`      | PostgreSQL connection settings (`HOST`, `PORT`, `DB`, `USER`, `PASSWORD`)                                                         |
| `QDRANT_URL`      | Qdrant service URL                                                                                                                |
| `QDRANT_API_KEY`  | Qdrant authentication key                                                                                                         |
| `LLM_BASE_URL`    | OpenAI-compatible API base URL (e.g. `https://api.openai.com/v1`, or `.../v1` for Ollama/vLLM)                                    |
| `LLM_EMBEDDING_MODEL` | Embedding model used for chunk indexing and query encoding (must match the Qdrant collection's vector size)                   |

**Optional / with defaults:**

| Variable                                 | Default                 | Description                                                         |
|------------------------------------------|-------------------------|---------------------------------------------------------------------|
| `ENV`                                    | `prod`                  | Set to `dev` to enable admin routes in API docs                     |
| `ROOT_PATH`                              | `/api/v1`               | API root path when running behind a reverse proxy                   |
| `REDIS_URL`                              | `redis://redis:6379`    | Redis URL for rate limiting counters                                |
| `RATE_LIMIT_DEFAULT_REQUESTS_PER_MINUTE` | `60`                    | Default rate limit for new users (`0` = unlimited)                  |
| `TRUSTED_PROXY_IPS`                      | _(empty)_               | Comma-separated IPs whose `X-Forwarded-For` header is trusted       |
| `QDRANT_COLLECTION_NAME`                 | `global_knowledge_base` | Qdrant collection for document chunks                               |
| `LLM_API_KEY`                            | _(empty)_               | API key sent to the LLM provider (optional for keyless local servers) |
| `LLM_TIMEOUT_SECONDS`                    | `30`                    | Timeout for LLM chat and embedding requests                         |
| `BOOTSTRAP_ADMIN_NAME`                   | `default_admin`         | Username for the auto-created admin account                         |
| `BOOTSTRAP_ADMIN_API_KEY_NAME`           | `admin1`                | API key name for the bootstrap admin key                            |
| `BOOTSTRAP_ADMIN_API_KEY`                | _(auto-generated)_      | Fixed bootstrap admin key — if unset, a key is generated and logged |
| `DOCUMENT_UPLOAD_MAX_BYTES`              | `10485760` (10 MB)      | Maximum size for uploaded documents                                 |
| `DOCUMENT_CHUNK_MAX_CHARS`               | `2500`                  | Maximum characters per document chunk                               |
| `DOCUMENT_CHUNK_OVERLAP_CHARS`           | `250`                   | Overlap between consecutive chunks                                  |
| `RAG_RETRIEVAL_LIMIT`                    | `10`                    | Number of chunks retrieved per chat request                         |
| `RAG_CONTEXT_MAX_CHARS`                  | `12000`                 | Max total context characters injected into the prompt               |

## Development

```bash
# Install all dependency groups (api, migrate, dev)
make setup

# Install Git hooks (ruff, ty, pytest run on commit)
make hooks

# Lint, type-check, and format
make check
make format

# Run tests
make test
```

Project layout:

```
src/rag_service/
├── api_keys/       # API key hashing, validation, and management
├── chats/          # Chat completions route, streaming, and usage logging
├── documents/      # Document ingestion, chunking, and search
├── llm_models/     # LLM model records (name, context size, etc.)
├── redis/          # Redis client and sliding-window rate limiter
├── security/       # Auth dependencies and AuthContext
├── users/          # User management and roles
├── config.py       # Settings (pydantic-settings)
├── middlewares.py  # Request logging and correlation ID middleware
└── main.py         # FastAPI app entrypoint
migrations/         # Alembic migration files
tests/              # pytest test suite
```

Admin and dev-only routes are included in the OpenAPI schema only when `ENV=dev`.

## Testing

The test suite uses `pytest` with `anyio` for async tests and `httpx` for HTTP-level testing.

```bash
make test      # run all tests
make coverage  # run all tests with a coverage report
make check     # lint + format check + type check
```

CI runs the suite with coverage on every push and pull request; the
[`python-coverage-comment-action`](https://github.com/py-cov-action/python-coverage-comment-action)
posts a coverage summary on pull requests and refreshes the coverage badge above.

Coverage areas:

| Area                   | What is tested                                                                                              |
|------------------------|-------------------------------------------------------------------------------------------------------------|
| **Rate limiter**       | Allowed/blocked responses, unlimited bypass, fail-open on Redis error, argument correctness, unique members |
| **Auth dependencies**  | Admin and user key validation, role enforcement, missing/invalid headers                                    |
| **Chat routes (HTTP)** | 401 without auth, 401 with invalid key, 429 when rate limited                                               |
| **Middleware**         | Trusted-proxy IP resolution, `X-Forwarded-For` chain parsing, correlation ID passthrough                    |
| **Document services**  | Hashing, chunking, overlap, indexing, vector search                                                         |
| **Chat services**      | RAG prompt building, streaming, timeouts, usage callbacks                                                   |
| **Schema validation**  | Request/response models, expiration date constraints                                                        |
| **OpenAPI schema**     | Auth responses, 4xx codes, and protected route documentation                                                |

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

**Admin endpoints** (visible in docs when `ENV=dev`):

| Resource             | Operations                                          |
|----------------------|-----------------------------------------------------|
| Users                | Create, list, get, update, delete                   |
| API keys             | Create, list per user                               |
| LLM models           | Create, list, get, update, delete                   |
| Documents            | Upload, list, get, search, delete                   |
| Chat completion logs | List with filters (user, model, status, date range) |

Admin list endpoints (users, API keys, LLM models, documents, chat completion logs) are paginated
via `limit` (1–100, default 50) and `offset` (default 0) query parameters and return `total`,
`limit`, and `offset` alongside the items.

## Roadmap

- [ ] Add summary usage endpoint for aggregate request, token, latency, and error metrics.
- [ ] Add PostgreSQL integration tests for migrations, relationships, and soft delete behaviour.
- [ ] Improve streaming interruption handling with explicit integration coverage.
- [ ] Support multiple knowledge bases per user or organisation (multi-tenancy).

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
