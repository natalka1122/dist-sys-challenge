from asyncio import Event

from ggstate import GGState
from logging_config import get_logger
from messages.body import Body
from messages.body_read import BodyRead, BodyReadOk

logger = get_logger(__name__)


def process_read(body: Body, gg_state: GGState, shutdown_event: Event) -> Body | None:
    if not isinstance(body, BodyRead):
        logger.error(f"Got body = {type(body)} {body}")
        shutdown_event.set()
        return None
    return BodyReadOk(messages=list(gg_state.broadcast))
