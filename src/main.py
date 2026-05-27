#!/usr/bin/env python3

import asyncio
import signal
import sys
from functools import partial

from logging_config import get_logger, setup_logging
from gossip_gloomers_app import gossip_gloomers_app

logger = get_logger(__name__)


def _signal_handler(shutdown_event: asyncio.Event) -> None:
    logger.info("Received exit signal, shutting down...")
    shutdown_event.set()


def setup_signal_handlers(shutdown_event: asyncio.Event) -> None:
    """Attach SIGINT and SIGTERM handlers"""
    loop = asyncio.get_running_loop()
    if sys.platform == "win32":  # pragma: no cover
        for sig in (signal.SIGINT, signal.SIGTERM):  # noqa: WPS426
            signal.signal(sig, lambda *_: shutdown_event.set())
    else:
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, partial(_signal_handler, shutdown_event))


async def main() -> None:
    shutdown_event = asyncio.Event()
    setup_signal_handlers(shutdown_event)
    setup_logging(level="DEBUG", log_dir="logs")
    await gossip_gloomers_app(
        shutdown_event=shutdown_event,
    )


if __name__ == "__main__":
    asyncio.run(main())
