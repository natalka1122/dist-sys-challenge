import json
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field

from const import MessageType
from exceptions import BadMessageError, NeedMoreBytesError

# @dataclass
# class Body:
#     type: MessageType


#     @classmethod
#     def from_json(cls, raw_json: dict[Any, Any]) -> "Body":
#         return Body(type=MessageType.ECHO)
class EchoBody(BaseModel):
    type: MessageType
    msg_id: int
    echo: str


@dataclass
class Message:
    src: str
    dst: str
    body: Body

    @classmethod
    def from_bytes(cls, raw_bytes: bytes) -> "Message":
        try:
            raw_json = json.loads(raw_bytes)
        except json.JSONDecodeError:
            raise NeedMoreBytesError
        src = raw_json.get("src")
        dst = raw_json.get("dst")
        body = raw_json.get("body")
        if not isinstance(src, str) or not isinstance(dst, str) or not isinstance(body, dict):
            raise BadMessageError
        return Message(src=src, dst=dst, body=Body.from_json(body))
