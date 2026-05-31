import asyncio
import logging
import sys
from typing import TextIO


class AsyncioContextFilter(logging.Filter):
    """Add asyncio task information to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        # Add current task name if available
        try:
            task = asyncio.current_task()
        except RuntimeError:
            task = None

        if task:
            record.task_name = task.get_name()
        else:
            record.task_name = "main"

        return True


def setup_logging(level: str) -> None:
    log_level: int = getattr(logging, level.upper())

    # Create root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    # Clear any existing handlers
    logger.handlers.clear()

    logger.addHandler(create_console_handler(level=log_level))

    # Reduce noise from common libraries
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module/component."""
    return logging.getLogger(name)


def create_console_handler(level: int) -> logging.StreamHandler[TextIO]:
    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)
    console_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(task_name)s] %(levelname)-8s %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        )
    )

    # Add asyncio context filter if requested
    console_handler.addFilter(AsyncioContextFilter())

    return console_handler
