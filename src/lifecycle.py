from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.log_config import get_log

log = get_log(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting application...")
    yield
    log.info("Application shut down")
