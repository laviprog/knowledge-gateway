from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from knowledge_gateway.config import settings
from knowledge_gateway.exceptions import setup_exception_handlers
from knowledge_gateway.lifecycle import lifespan
from knowledge_gateway.log_config import configure as configure_logging
from knowledge_gateway.middlewares import LogMiddleware
from knowledge_gateway.routes import routes_register

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
