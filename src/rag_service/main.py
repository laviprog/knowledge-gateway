from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from rag_service.config import settings
from rag_service.exceptions import setup_exception_handlers
from rag_service.lifecycle import lifespan
from rag_service.log_config import configure as configure_logging
from rag_service.middlewares import LogMiddleware
from rag_service.routes import routes_register

configure_logging()

app = FastAPI(
    title="Knowledge Gateway API",
    version="0.2.1",
    docs_url="/docs/swagger",
    openapi_url="/openapi.json",
    root_path=settings.ROOT_PATH,
    lifespan=lifespan,
)

setup_exception_handlers(app)

app.add_middleware(LogMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Expose Prometheus metrics at /metrics (HTTP RED metrics + custom collectors).
Instrumentator(excluded_handlers=["/metrics", "/healthcheck"]).instrument(app).expose(
    app, include_in_schema=False
)

routes_register(app)
