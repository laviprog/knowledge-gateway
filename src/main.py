from fastapi import FastAPI

from src.config import settings
from src.exceptions import setup_exception_handlers
from src.lifecycle import lifespan
from src.log_config import configure as configure_logging
from src.middlewares import LogMiddleware
from src.routes import routes_register

configure_logging()

app = FastAPI(
    title="RAG Service API",
    version="0.1.0",
    docs_url="/docs/swagger",
    openapi_url="/openapi.json",
    root_path=settings.ROOT_PATH,
    lifespan=lifespan,
)

setup_exception_handlers(app)

app.add_middleware(LogMiddleware)

routes_register(app)
