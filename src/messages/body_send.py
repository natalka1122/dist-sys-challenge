from dataclasses import dataclass
from typing import Any

from const import MessageType
from exceptions import BadMessageError
from messages.body import Body


@dataclass(kw_only=True, frozen=True)
class BodySend(Body):
    type: MessageType = MessageType.SEND
    msg: int

    @classmethod
    def from_json(cls, body_json: dict[Any, Any]) -> BodySend:
        msg = body_json.get("msg")
        if not isinstance(msg, int):
            raise BadMessageError(f"Bad msg = {type(msg)} {msg} body_json = {body_json}")
        return BodySend(msg=msg)


@dataclass(kw_only=True, frozen=True)
class BodySendOk(Body):
    type: MessageType = MessageType.SEND_OK

    @classmethod
    def from_json(cls, body_json: dict[Any, Any]) -> BodySendOk:
        return BodySendOk()
