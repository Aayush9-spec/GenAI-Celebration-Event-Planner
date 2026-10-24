from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/eventplanner"
    GEMINI_API_KEY: str = ""
    SECRET_KEY: str = "changeme-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ALLOWED_ORIGINS: str = "*"
    PROJECT_NAME: str = "Celebration & Event Planner"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
