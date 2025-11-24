import logging
from typing import Optional

from .config import Settings


def setup_logging(settings: Settings) -> None:
    """Configure stdlib logging according to settings.

    - Level controlled by settings.LOG_LEVEL
    - Simple, readable format
    """
    level_name = (settings.LOG_LEVEL or "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )

    # Optionally tune noisy loggers here
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.INFO)
    logging.getLogger("langchain").setLevel(logging.INFO)
    logging.getLogger("langgraph").setLevel(logging.INFO)

    logging.getLogger(__name__).info("Logging configured at level %s", level_name)
