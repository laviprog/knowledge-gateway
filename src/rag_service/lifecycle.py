from contextlib import asynccontextmanager

from fastapi import FastAPI

from rag_service.bootstrap import create_default_admin
from rag_service.log_config import get_log
from rag_service.ollama.client import close_ollama_client
from rag_service.qdrant.client import close_qdrant_client
from rag_service.redis.client import close_redis_pool

log = get_log(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting application...")
    await create_default_admin()
    try:
        yield
    finally:
        await close_ollama_client()
        await close_qdrant_client()
        await close_redis_pool()
        log.info("Application shut down")
