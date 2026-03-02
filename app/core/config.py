from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENV: str = "local"
    APP_NAME: str = "rate-limit-platform"
    APP_SECRET: str = "change-me"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/rate_limit_db"
    REDIS_URL: str = "redis://localhost:6379/0"


settings = Settings()