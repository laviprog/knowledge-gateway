from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from rag_service.config import settings
from rag_service.exceptions import setup_exception_handlers
from rag_service.lifecycle import lifespan
from rag_service.log_config import configure as configure_logging
from rag_service.middlewares import LogMiddleware
from rag_service.routes import routes_register

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

routes_register(app)
