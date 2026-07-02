from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    chroma_persist_dir: str = "./chroma_db"
    dashscope_api_key: str = ""
    dashscope_base_url: str = ""
    qwen_model: str = "qwen3.5-122b-a10b"
    dashscope_embedding_model: str = "text-embedding-v4"
    upload_dir: str = "./uploads"
    summary_dir: str = "./summaries"
    max_upload_mb: int = 50
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    app_assistant_name: str = "AI Book Assistant"
    app_assistant_description: str = (
        "AI assistant for summarizing books and answering questions using "
        "uploaded book content."
    )
    app_creator_name: str = ""
    app_creator_description: str = ""
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
