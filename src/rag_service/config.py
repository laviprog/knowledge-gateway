from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or a .env file.
    """

    model_config = SettingsConfigDict(env_file=".env")

    LOG_LEVEL: str = "DEBUG"  # DEBUG | INFO | WARNING | ERROR | CRITICAL
    ENV: str = "dev"  # dev | prod

    ROOT_PATH: str = "/api/v1"  # API root path

    API_KEY_PEPPER: str = "some_random_pepper_value"  # Used for hashing API keys
    API_KEY_DEFAULT_PREFIX: str = "syn_rag"  # Default prefix for generated API keys

    BOOTSTRAP_ADMIN_NAME: str = "default_admin"
    BOOTSTRAP_ADMIN_API_KEY_NAME: str = "admin1"
    BOOTSTRAP_ADMIN_API_KEY: str | None = None

    DOCUMENT_UPLOAD_MAX_BYTES: int = 10 * 1024 * 1024  # Maximum allowed size 10 MB
    DOCUMENT_CHUNK_MAX_CHARS: int = 2500
    DOCUMENT_CHUNK_OVERLAP_CHARS: int = 250
    RAG_RETRIEVAL_LIMIT: int = 10
    RAG_CONTEXT_MAX_CHARS: int = 12000

    # Database configuration
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    # Qdrant configuration
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION_NAME: str = "global_knowledge_base"

    # Ollama configuration
    OLLAMA_BASE_URL: str
    OLLAMA_API_KEY: str | None = None
    OLLAMA_EMBEDDING_MODEL: str = "embeddinggemma"
    OLLAMA_TIMEOUT_SECONDS: float = 30
    OLLAMA_KEEP_ALIVE: str = "24h"

    @property
    def _DB_URL_BASE(self) -> str:
        return (
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def DB_URL_ASYNC(self) -> str:
        return f"postgresql+asyncpg://{self._DB_URL_BASE}"

    @property
    def DB_URL_SYNC(self) -> str:
        return f"postgresql+psycopg2://{self._DB_URL_BASE}"


settings = Settings()  # ty: ignore[missing-argument]
