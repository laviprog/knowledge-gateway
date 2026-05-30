from contextlib import asynccontextmanager

from fastapi import FastAPI

from rag_service.bootstrap import create_default_admin
from rag_service.log_config import get_log

log = get_log(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting application...")
    await create_default_admin()
    yield
    log.info("Application shut down")
