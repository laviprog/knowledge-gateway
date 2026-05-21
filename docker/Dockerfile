FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --group api --no-install-project

COPY . .

CMD ["uv", "run", "--no-dev", "--group", "api", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
