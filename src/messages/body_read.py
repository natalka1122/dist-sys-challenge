from dataclasses import dataclass
from typing import Any

from const import MessageType
from logging_config import get_logger
from messages.body import Body
from messages.func import get_list_with_int

logger = get_logger(__name__)


@dataclass(kw_only=True, frozen=True)
class BodyRead(Body):
    type: MessageType = MessageType.READ

    @classmethod
    def from_json(cls, body_json: dict[Any, Any]) -> BodyRead:
        return BodyRead()


@dataclass(kw_only=True, frozen=True)
class BodyReadOk(Body):
    type: MessageType = MessageType.READ_OK
    messages: list[int]

    @classmethod
    def from_json(cls, body_json: dict[Any, Any]) -> BodyReadOk:
        messages = get_list_with_int(body_json, "messages")
        return BodyReadOk(messages=messages)
