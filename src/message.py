import json
from dataclasses import dataclass
from typing import Any

from const import ErrorType, MessageType
from exceptions import BadMessageError, NeedMoreBytesError
from logging_config import get_logger

logger = get_logger(__name__)


def _get_msg_id(raw_json: dict[Any, Any]) -> int:
    msg_id = raw_json.get("msg_id")
    if not isinstance(msg_id, int):
        raise BadMessageError(f"raw_json = {raw_json} msg_id = {msg_id}")
    return msg_id


@dataclass
class Body:
    type: MessageType

    def to_json(self) -> dict[str, Any]:
        return {"type": self.type}

    @classmethod
    def from_json(cls, raw_json: dict[Any, Any]) -> "Body":
        body_type = raw_json.get("type")
        if body_type == MessageType.ECHO:
            return EchoBody(msg_id=_get_msg_id(raw_json), echo=raw_json.get("echo", ""))
        elif body_type == MessageType.INIT:
            return InitBody(msg_id=_get_msg_id(raw_json))
        return ErrorBody(
            code=ErrorType.NOT_SUPPORTED,
            in_reply_to=raw_json.get("msg_id", 0),
            text=f"Unknown body_type = {body_type} raw_json = {raw_json}",
        )


@dataclass(kw_only=True)
class EchoBody(Body):
    msg_id: int
    echo: str
    type: MessageType = MessageType.ECHO

    def to_json(self) -> dict[str, Any]:
        result = super().to_json()
        result["msg_id"] = self.msg_id
        result["echo"] = self.echo
        return result


@dataclass(kw_only=True)
class EchoOkBody(Body):
    msg_id: int
    echo: str
    in_reply_to: int
    type: MessageType = MessageType.ECHO_OK

    def to_json(self) -> dict[str, Any]:
        result = super().to_json()
        result["msg_id"] = self.msg_id
        result["echo"] = self.echo
        result["in_reply_to"] = self.in_reply_to
        return result


@dataclass(kw_only=True)
class InitBody(Body):
    msg_id: int
    type: MessageType = MessageType.INIT

    def to_json(self) -> dict[str, Any]:
        result = super().to_json()
        result["msg_id"] = self.msg_id
        return result


@dataclass(kw_only=True)
class InitOkBody(Body):
    in_reply_to: int
    type: MessageType = MessageType.INIT_OK

    def to_json(self) -> dict[str, Any]:
        result = super().to_json()
        result["in_reply_to"] = self.in_reply_to
        return result


@dataclass(kw_only=True)
class ErrorBody(Body):
    in_reply_to: int
    text: str
    code: ErrorType
    type: MessageType = MessageType.ERROR

    def to_json(self) -> dict[str, Any]:
        result = super().to_json()
        result["in_reply_to"] = self.in_reply_to
        result["code"] = self.code
        result["text"] = self.text
        return result


@dataclass
class Message:
    src: str
    dest: str
    body: Body

    def to_bytes(self) -> bytes:
        result: dict[str, Any] = {"src": self.src, "dest": self.dest, "body": self.body.to_json()}
        return json.dumps(result).encode()

    @classmethod
    def from_bytes(cls, raw_bytes: bytes) -> "Message":
        try:
            raw_json = json.loads(raw_bytes)
        except json.JSONDecodeError:
            raise NeedMoreBytesError
        src = raw_json.get("src")
        dest = raw_json.get("dest")
        body = raw_json.get("body")
        if not isinstance(src, str) or not isinstance(dest, str) or not isinstance(body, dict):
            raise BadMessageError
        return Message(src=src, dest=dest, body=Body.from_json(body))
