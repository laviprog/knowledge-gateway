from rag_service.config import settings
from rag_service.database.config import sqlalchemy_config
from rag_service.log_config import get_log
from rag_service.users.services import UserService

log = get_log(__name__)


async def create_default_admin() -> None:
    log.info("Creating default admin...")
    async with UserService.new(config=sqlalchemy_config) as service:
        existing_admin = await service.get_one_or_none(name=settings.BOOTSTRAP_ADMIN_NAME)
        if existing_admin:
            log.info("Admin already exists", name=existing_admin.name)
        else:
            admin, api_key_value = await service.create_admin_with_api_key(
                name=settings.BOOTSTRAP_ADMIN_NAME,
                api_key_name=settings.BOOTSTRAP_ADMIN_API_KEY_NAME,
                api_key_value=settings.BOOTSTRAP_ADMIN_API_KEY,
            )
            log.info(
                "Admin has been created",
                user_id=str(admin.id),
                name=admin.name,
            )

            if settings.BOOTSTRAP_ADMIN_API_KEY:
                log.info("Bootstrap admin API key has been loaded from configuration")
            else:
                log.warning(
                    "Bootstrap admin API key was auto-generated. "
                    "Set BOOTSTRAP_ADMIN_API_KEY in .env to fix the key across restarts. "
                    "Retrieve the current key from the database (api_keys.key_prefix column).",
                    key_prefix=api_key_value[:12],
                )
