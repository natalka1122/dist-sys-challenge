from dataclasses import dataclass
from typing import Any, cast

from const import MessageType
from exceptions import BadMessageError
from logging_config import get_logger
from messages.body import Body

logger = get_logger(__name__)


@dataclass(kw_only=True, frozen=True)
class BodyInit(Body):
    type: MessageType = MessageType.INIT
    node_id: str
    node_ids: list[str]

    @classmethod
    def from_json(cls, body_json: dict[Any, Any]) -> BodyInit:
        node_id = body_json.get("node_id")
        if not isinstance(node_id, str):
            raise BadMessageError(
                f"Bad node_id = {type(node_id)} {node_id} body_json = {body_json}"
            )
        node_ids = body_json.get("node_ids")
        if not isinstance(node_ids, list):
            raise BadMessageError(
                f"Bad node_ids = {type(node_ids)} {node_ids} body_json = {body_json}"
            )
        node_ids = cast(list[str], node_ids)
        if not all(
            isinstance(k, str) for k in node_ids  # pyright: ignore[reportUnnecessaryIsInstance]
        ):
            raise BadMessageError(f"Wrong node_ids = {node_ids} body_json = {body_json}")
        return BodyInit(node_id=node_id, node_ids=node_ids)


@dataclass(kw_only=True, frozen=True)
class BodyInitOk(Body):
    type: MessageType = MessageType.INIT_OK

    @classmethod
    def from_json(cls, body_json: dict[Any, Any]) -> BodyInitOk:
        return BodyInitOk()
