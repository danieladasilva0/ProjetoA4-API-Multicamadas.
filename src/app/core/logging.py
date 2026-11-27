import sys

from loguru import logger


def configure_logging() -> None:
    """Emite logs estruturados em JSON para stdout."""
    logger.remove()
    logger.add(sys.stdout, level="INFO", serialize=True, backtrace=False, diagnose=False)
