from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Strategic context
    AXIS_OF_EXPLORATION: str = ""
    UNIT_OF_ANALYSIS: str = ""
    COUNTRY: str = ""

    # Behaviour toggles
    EXTERNAL_RESEARCH: bool = False  # default: no external research
    # Free-text constraints description (e.g. "limited capital, MVP ≤ 60 days")
    CONSTRAINTS: str = ""
    COMPLEX_UNIT: bool = False

    # Whether to use a static TODO plan (true) or dynamic planning (future use)
    STATIC_TODO: bool = True

    # Number of roles to infer in step 2
    IDEAL_ROLES: int = 7

    # Base directory where run artefacts will be stored (can be relative or absolute)
    OUTPUT_BASE_DIR: str = "runs"

    # API keys
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    TAVILY_API_KEY: str = ""

    # LangChain / LangSmith
    LANGCHAIN_TRACING: bool = False
    LANGCHAIN_PROJECT: str = "langgraph-finance-project"
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_TRACING: bool = False
    LANGCHAIN_TRACING_V2: bool = False
    LANGSMITH_PROJECT: str = "deep-agents-from-scratch"
    # New: endpoint field to match your .env
    LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com"

    # App environment
    ENVIRONMENT: str = "dev"
    DEBUG: bool = True

    # Optional DB URL
    DATABASE_URL: str = "sqlite:///./app.db"

    # Logging
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Important: don't crash when .env has extra keys
        extra = "ignore"
