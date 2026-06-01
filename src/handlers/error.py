from asyncio import Event

from ggstate import GGState
from logging_config import get_logger
from messages.body import Body
from messages.body_error import BodyError

logger = get_logger(__name__)


def process_error(  # noqa: WPS324
    body: Body, gg_state: GGState, shutdown_event: Event
) -> Body | None:
    if not isinstance(body, BodyError):
        logger.error(f"Got body = {type(body)} {body}")
        shutdown_event.set()
        return None
    logger.error(f"Got Error message: {body}")
    return None
