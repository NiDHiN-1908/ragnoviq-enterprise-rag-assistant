"""
Configuration module for RAGNoviq application.
Handles environment variables and application settings using Pydantic.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False
    environment: str = "development"

    # LLM Configuration
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.3-70b-versatile"
    google_api_key: Optional[str] = None
    gemini_model: str = "gemini-1.5-flash"
    llm_provider: str = "groq"  # groq or gemini

    # Embeddings Configuration
    embeddings_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Vector Database Configuration
    vector_db_type: str = "faiss"  # faiss or chromadb
    vector_db_path: str = "./data/vector_db"
    chunk_size: int = 512
    chunk_overlap: int = 102

    # Web Scraping Configuration
    max_crawl_depth: int = 5
    max_pages_per_domain: int = 100
    request_timeout: int = 30
    user_agent: str = "RAGNoviq/1.0 (+https://ragnoviq.ai)"
    enable_javascript: bool = False

    # Database Configuration
    database_url: str = "sqlite:///./data/ragnoviq.db"
    database_echo: bool = False

    # API Security
    api_key_header: str = "X-API-Key"
    rate_limit_requests: int = 100
    rate_limit_period: int = 3600

    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "./logs/ragnoviq.log"

    # Redis Configuration
    redis_url: Optional[str] = None
    enable_cache: bool = True
    cache_ttl: int = 3600

    # Retrieval Configuration
    top_k_chunks: int = 5
    similarity_threshold: float = 0.5
    use_metadata_filter: bool = True

    # Processing Configuration
    enable_async_processing: bool = True
    max_workers: int = 4
    batch_size: int = 32

    # Frontend Configuration
    frontend_url: str = "http://localhost:3000"
    cors_origins: list = ["http://localhost:3000", "http://localhost:8000"]

    # Monitoring
    enable_telemetry: bool = False
    sentry_dsn: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
