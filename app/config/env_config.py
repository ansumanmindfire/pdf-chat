"""Environment settings manager using python-dotenv and os.getenv."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application configuration settings loaded via os.getenv."""

    # Project Metadata
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "PDF Chat RAG API")
    PROJECT_VERSION: str = os.getenv("PROJECT_VERSION", "1.0.0")
    PROJECT_DESCRIPTION: str = os.getenv(
        "PROJECT_DESCRIPTION",
        "Production-ready RAG application using FastAPI, LangChain, FAISS, SQLite, and Google Gemini.",
    )

    # Environment & Logging
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "DEVELOPMENT")
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")

    # API Keys & Models
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-3.6-flash")

    # Storage Paths & Directories
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/pdf_chat.db")
    FAISS_INDEX_PATH: str = os.getenv("FAISS_INDEX_PATH", "data/faiss_index")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "data/uploads")

    # RAG & File Upload Constraints
    K_RETRIEVAL: int = int(os.getenv("K_RETRIEVAL", "3"))
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "20"))


# Global settings instance
settings = Settings()
