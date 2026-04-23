from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str | None = None
    TURSO_DATABASE_URL: str | None = None
    TURSO_AUTH_TOKEN: str | None = None
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    FRONTEND_ORIGINS: str = "http://localhost:5173"
    ENABLE_SCHEDULER: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
