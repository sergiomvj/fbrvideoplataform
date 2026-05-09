from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://synkra:synkra@localhost:5432/synkra"
    REDIS_URL: str = "redis://localhost:6379/0"
    SESSION_SECRET: str = ""
    BACKEND_INTERNAL_TOKEN: str = ""
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
    ENABLE_DOCS: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}
