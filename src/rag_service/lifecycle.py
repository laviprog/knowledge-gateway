from contextlib import asynccontextmanager

from fastapi import FastAPI

from rag_service.database.config import sqlalchemy_config
from rag_service.log_config import get_log
from rag_service.users.services import UserService

log = get_log(__name__)


async def _create_default_admin(name: str = "default_admin") -> None:
    log.info("Creating default admin...")
    async with UserService.new(config=sqlalchemy_config) as service:
        existing_admin = await service.get_one_or_none(name=name)
        if existing_admin:
            log.info("Admin already exists", name=existing_admin.name)
        else:
            admin, api_key_value = await service.create_admin_with_api_key(name=name)
            log.info(
                "Admin has been created",
                user_id=str(admin.id),
                name=name,
                api_key_value=api_key_value,
            )


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting application...")
    await _create_default_admin()
    yield
    log.info("Application shut down")
