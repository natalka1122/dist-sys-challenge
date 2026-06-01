from asyncio import Event

from ggstate import GGState
from logging_config import get_logger
from messages.body import Body
from messages.body_echo import BodyEcho, BodyEchoOk

logger = get_logger(__name__)


def process_echo(body: Body, gg_state: GGState, shutdown_event: Event) -> Body | None:
    if not isinstance(body, BodyEcho):
        logger.error(f"Got body = {type(body)} {body}")
        shutdown_event.set()
        return None

    return BodyEchoOk(echo=body.echo)
