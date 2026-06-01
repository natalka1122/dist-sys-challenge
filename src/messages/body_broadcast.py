from dataclasses import dataclass
from typing import Any

from const import MessageType
from messages.body import Body
from messages.func import get_int


@dataclass(kw_only=True, frozen=True)
class BodyBroadcast(Body):
    type: MessageType = MessageType.BROADCAST
    message: int

    @classmethod
    def from_json(cls, body_json: dict[Any, Any]) -> BodyBroadcast:
        message = get_int(body_json, "message")
        return BodyBroadcast(message=message)


@dataclass(kw_only=True, frozen=True)
class BodyBroadcastOk(Body):
    type: MessageType = MessageType.BROADCAST_OK

    @classmethod
    def from_json(cls, body_json: dict[Any, Any]) -> BodyBroadcastOk:
        return BodyBroadcastOk()
