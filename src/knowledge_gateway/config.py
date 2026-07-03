from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or a .env file.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    LOG_LEVEL: str = "DEBUG"  # DEBUG | INFO | WARNING | ERROR | CRITICAL
    ENV: str = "dev"  # dev | prod

    ROOT_PATH: str = "/api/v1"  # API root path

    API_KEY_PEPPER: str  # Used for hashing API keys — must be set explicitly, no default
    API_KEY_DEFAULT_PREFIX: str = "kg"  # Default prefix for generated API keys

    # Symmetric key used to encrypt provider API keys at rest (any string; a Fernet key is
    # derived from it). Required only when a provider record stores an api_key.
    PROVIDER_SECRET_KEY: str | None = None

    # Comma-separated list of trusted reverse-proxy IPs whose X-Forwarded-For header is trusted
    TRUSTED_PROXY_IPS: list[str] = []

    # Redis configuration (used for per-user rate limiting)
    REDIS_URL: str = "redis://localhost:6379"

    # Default rate limit for new users (0 = unlimited)
    RATE_LIMIT_DEFAULT_REQUESTS_PER_MINUTE: int = 60

    BOOTSTRAP_ADMIN_NAME: str = "default_admin"
    BOOTSTRAP_ADMIN_API_KEY_NAME: str = "admin1"
    BOOTSTRAP_ADMIN_API_KEY: str | None = None
    # Password for the bootstrap admin's interactive (admin panel) login. When set, it is applied
    # to the default admin on startup (created or updated). Leave unset to disable password login.
    BOOTSTRAP_ADMIN_PASSWORD: str | None = None

    # Interactive session auth (admin panel). Sessions are opaque tokens stored in Redis and
    # carried in an httpOnly cookie — the raw token never reaches JavaScript.
    SESSION_COOKIE_NAME: str = "knowledge_gateway_admin_session"
    SESSION_TTL_SECONDS: int = 60 * 60 * 8  # 8 hours; TTL slides on each authenticated request
    SESSION_COOKIE_SECURE: bool = True  # set False for local dev over plain HTTP
    SESSION_COOKIE_SAMESITE: str = "strict"  # strict | lax | none

    DOCUMENT_UPLOAD_MAX_BYTES: int = 10 * 1024 * 1024  # Maximum allowed size 10 MB
    DOCUMENT_CHUNK_MAX_CHARS: int = 2500
    DOCUMENT_CHUNK_OVERLAP_CHARS: int = 250
    RAG_RETRIEVAL_LIMIT: int = 10
    RAG_CONTEXT_MAX_CHARS: int = 12000
    # Minimum similarity score a retrieved chunk must reach to be used as context. ``None``
    # disables score filtering. A knowledge base may override this with its own ``min_score``.
    RAG_MIN_SCORE: float | None = None
    # Default system instruction prepended to the RAG prompt. A knowledge base may override this
    # with its own ``system_prompt``.
    RAG_SYSTEM_INSTRUCTION: str = (
        "Use the knowledge base context below to answer the user.\n"
        "If the context does not contain enough information, say that the information is "
        "insufficient.\n"
        "Keep the answer concise and accurate."
    )

    # Database configuration
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    # Qdrant configuration
    QDRANT_URL: str
    QDRANT_API_KEY: str

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
