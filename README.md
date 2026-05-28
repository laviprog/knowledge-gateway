# RAG Service

...

## 🛠️ Getting Started

Follow the steps below to set up and run the service using Docker

### ⚙️ Configure Environment Variables

Copy the example environment file and fill in the necessary values:

```bash
cp .env.example .env
```

Edit the `.env` file to set your environment variables. You can use the default values or customize
them as needed.

Also, make sure to configure the `docker-compose.yml` file if necessary.

### 🐳 Build and Run the Docker Container

Start the Docker container with the following commands:

```bash
docker compose build
```

```bash
docker compose up -d
```

This command will build the Docker image and start the container.

## Development setup

Install dependencies:

```bash
uv sync --all-groups
```

Install Git hooks:

```bash
uv run pre-commit install
```

Run checks manually:

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check
```

Run all pre-commit hooks manually:

```bash
uv run pre-commit run --all-files
```

### Commit workflow

Before every commit, pre-commit automatically runs:

- `ruff check --fix`
- `ruff format`
- `ty check`

If Ruff modifies files, the commit will stop. Review changes, stage them again, and rerun commit:

```bash
git add .
git commit -m "your message"
```
