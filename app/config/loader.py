from dotenv import load_dotenv

from .settings import Settings


def load_settings() -> Settings:
    """Load environment variables and return a Settings instance.

    This is the single entry point for configuration across the app.
    """
    # Ensure .env is loaded (if present)
    load_dotenv()
    return Settings()
