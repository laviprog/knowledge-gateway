FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app
ENV PYTHONPATH=/app/src

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-default-groups --group api --no-install-project

COPY . .

CMD ["uv", "run", "--no-default-groups", "--group", "api", "uvicorn", "rag_service.main:app", "--host", "0.0.0.0", "--port", "8080"]
