from asyncio import Event

from ggstate import GGState
from logging_config import get_logger
from messages.body import Body
from messages.body_send import BodySend, BodySendOk

logger = get_logger(__name__)


def process_send(body: Body, gg_state: GGState, shutdown_event: Event) -> Body | None:
    if not isinstance(body, BodySend):
        logger.error(f"Got body = {type(body)} {body}")
        shutdown_event.set()
        return None

    return BodySendOk()
