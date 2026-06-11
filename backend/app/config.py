from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "RevenueAI"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite:///./revenueai.db"

    STORAGE_BACKEND: str = "local"
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024

    SUPABASE_URL: str | None = None
    SUPABASE_SERVICE_KEY: str | None = None
    SUPABASE_STORAGE_BUCKET: str = "revenueai-uploads"

    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_MAX_TOKENS: int = 2000
    OPENAI_TEMPERATURE: float = 0.3

    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.5-flash"

    CORS_ORIGINS: str = "http://localhost:3000,https://revenue-ai-delta.vercel.app"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
