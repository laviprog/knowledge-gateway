import logging
import logging.config
from typing import Any, ClassVar

import structlog

from rag_service.config import settings
from rag_service.utils import is_dev_env

Logger = structlog.stdlib.BoundLogger


def get_level() -> str:
    return settings.LOG_LEVEL


class Logging[RendererType]:
    timestamper = structlog.processors.TimeStamper(fmt="iso")
    shared_processors: ClassVar[list[Any]] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        timestamper,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.StackInfoRenderer(),
    ]

    @classmethod
    def get_processors(cls) -> list[Any]:
        """
        Returns the list of processors to be used by structlog.
        """
        return [
            *cls.shared_processors,
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ]

    @classmethod
    def get_renderer(cls) -> RendererType:
        raise NotImplementedError()

    @classmethod
    def configure_stdlib(
        cls,
    ) -> None:
        """
        Configures the standard library logging.
        """
        level = get_level()

        logging.config.dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": True,
                # define the layout of log messages
                "formatters": {
                    "myLogger": {
                        "()": structlog.stdlib.ProcessorFormatter,
                        "processors": [
                            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                            cls.get_renderer(),
                        ],
                        "foreign_pre_chain": [
                            *cls.shared_processors,
                            structlog.processors.format_exc_info,
                        ],
                    },
                },
                "handlers": {
                    "default": {
                        "level": level,
                        "class": "logging.StreamHandler",
                        "formatter": "myLogger",
                    },
                },
                "loggers": {
                    "": {"handlers": ["default"], "level": level, "propagate": False},
                    "uvicorn": {"handlers": [], "level": "INFO", "propagate": True},
                    "uvicorn.error": {"handlers": [], "level": "INFO", "propagate": True},
                    "uvicorn.access": {"handlers": [], "level": "NOTSET", "propagate": False},
                    "sqlalchemy": {"handlers": [], "level": "WARNING", "propagate": True},
                },
            }
        )

    @classmethod
    def configure_structlog(cls) -> None:
        structlog.configure_once(
            processors=cls.get_processors(),
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

    @classmethod
    def configure(cls) -> None:
        cls.configure_stdlib()
        cls.configure_structlog()


class Production(Logging[structlog.processors.JSONRenderer]):
    """
    Production logging configuration using JSON renderer.
    """

    @classmethod
    def get_renderer(cls) -> structlog.processors.JSONRenderer:
        return structlog.processors.JSONRenderer(ensure_ascii=False)


class Development(Logging[structlog.dev.ConsoleRenderer]):
    """
    Development logging configuration using console renderer.
    """

    @classmethod
    def get_renderer(cls) -> structlog.dev.ConsoleRenderer:
        return structlog.dev.ConsoleRenderer()


def get_log(name: str | None = None) -> Logger:
    """
    Returns a logger configured with the given name.
    """
    return structlog.get_logger(name)


def configure() -> None:
    """
    Configures logging based on the environment settings.
    """
    if not is_dev_env():
        Production.configure()
    else:
        Development.configure()
    structlog.contextvars.bind_contextvars(service="rag-service")
