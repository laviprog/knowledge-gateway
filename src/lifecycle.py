from contextlib import asynccontextmanager

from fastapi import FastAPI

from src import log


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting application...")
    yield
    log.info("Application shut down")
