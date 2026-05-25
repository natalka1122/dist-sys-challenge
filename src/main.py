#!/usr/bin/env python3

import asyncio
import signal
import sys
from functools import partial
from typing import Callable

from logging_config import get_logger, setup_logging
from maelstrom_app import maelstrom_app

setup_logging(level="DEBUG", log_dir="logs")
logger = get_logger(__name__)


def _signal_handler(sig: signal.Signals, shutdown_event: asyncio.Event) -> None:
    logger.info(f"Received exit signal {sig.name}...")
    shutdown_event.set()


def make_signal_handler(sig: signal.Signals, shutdown_event: asyncio.Event) -> Callable[[], None]:
    return partial(_signal_handler, sig, shutdown_event)


def setup_signal_handlers(shutdown_event: asyncio.Event) -> None:
    """Attach SIGINT and SIGTERM handlers"""
    loop = asyncio.get_running_loop()
    if sys.platform == "win32":  # pragma: no cover
        for sig in (signal.SIGINT, signal.SIGTERM):  # noqa: WPS426
            signal.signal(sig, lambda *_: shutdown_event.set())
    else:
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, make_signal_handler(sig, shutdown_event))


async def main() -> None:
    started_event = asyncio.Event()
    shutdown_event = asyncio.Event()
    setup_signal_handlers(shutdown_event)
    await maelstrom_app(
        started_event=started_event,
        shutdown_event=shutdown_event,
    )


if __name__ == "__main__":
    asyncio.run(main())
