import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    """Application settings loaded from environment variables."""

    PROJECT_NAME: str = "Text-to-SQL API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Convert natural language questions into SQL queries"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/sample.db")

    # Gemini LLM
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

    # Safety
    MAX_QUERY_RESULTS: int = 100
    QUERY_TIMEOUT_SECONDS: int = 10


settings = Settings()
