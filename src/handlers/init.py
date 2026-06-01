from asyncio import Event

from ggstate import GGState
from logging_config import get_logger
from messages.body import Body
from messages.body_init import BodyInit, BodyInitOk

logger = get_logger(__name__)


def process_init(body: Body, gg_state: GGState, shutdown_event: Event) -> Body | None:
    if not isinstance(body, BodyInit):
        logger.error(f"Got body = {type(body)} {body}")
        shutdown_event.set()
        return None
    if isinstance(gg_state.node_id, str):
        logger.error(f"Got init but already have node_id = {gg_state.node_id}")
        shutdown_event.set()
        return None
    gg_state.node_id = body.node_id
    gg_state.node_ids = set(body.node_ids)
    return BodyInitOk()
