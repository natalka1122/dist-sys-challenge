from asyncio import Event

from ggstate import GGState
from logging_config import get_logger
from messages.body import Body
from messages.body_broadcast import BodyBroadcast, BodyBroadcastOk

logger = get_logger(__name__)


def process_broadcast(body: Body, gg_state: GGState, shutdown_event: Event) -> Body | None:
    if not isinstance(body, BodyBroadcast):
        logger.error(f"Got body = {type(body)} {body}")
        shutdown_event.set()
        return None
    gg_state.broadcast.add(body.message)
    return BodyBroadcastOk()
