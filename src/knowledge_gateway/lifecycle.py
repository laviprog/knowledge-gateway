from contextlib import asynccontextmanager

from fastapi import FastAPI

from knowledge_gateway.bootstrap import create_default_admin
from knowledge_gateway.llm.client import close_llm_clients
from knowledge_gateway.log_config import get_log
from knowledge_gateway.qdrant.client import close_qdrant_client
from knowledge_gateway.redis.client import close_redis_pool

log = get_log(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting application...")
    await create_default_admin()
    try:
        yield
    finally:
        await close_llm_clients()
        await close_qdrant_client()
        await close_redis_pool()
        log.info("Application shut down")
