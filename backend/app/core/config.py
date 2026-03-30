from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/saas_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    JWT_SECRET_KEY: str = "dev-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ASAAS_API_KEY: str = ""
    ASAAS_WEBHOOK_SECRET: str = ""
    ASAAS_ENVIRONMENT: str = "sandbox"
    BREVO_API_KEY: str = ""
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"
    PROJECT_NAME: str = "SaaS Boilerplate"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    SENTRY_DSN: str = ""


settings = Settings()
