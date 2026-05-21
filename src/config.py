from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or a .env file.
    """

    model_config = SettingsConfigDict(env_file=".env")

    LOG_LEVEL: str = "DEBUG"  # DEBUG | INFO | WARNING | ERROR | CRITICAL
    ENV: str = "dev"  # dev | prod

    ROOT_PATH: str = "/api/v1"  # API root path

    # Database configuration
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    # Qdrant configuration
    QDRANT_URL: str
    QDRANT_API_KEY: str

    # Ollama configuration
    OLLAMA_BASE_URL: str
    OLLAMA_API_KEY: str

    @property
    def _DB_URL_BASE(self) -> str:
        return f"{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DB_URL_ASYNC(self) -> str:
        return f"postgresql+asyncpg://{self._DB_URL_BASE}"

    @property
    def DB_URL_SYNC(self) -> str:
        return f"postgresql+psycopg2://{self._DB_URL_BASE}"


settings = Settings()  # ty: ignore[missing-argument]
