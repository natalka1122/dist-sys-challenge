from dataclasses import dataclass
from typing import Any

from const import MessageType
from exceptions import BadMessageError
from logging_config import get_logger
from messages.body import Body

logger = get_logger(__name__)


@dataclass(kw_only=True, frozen=True)
class BodyEcho(Body):
    type: MessageType = MessageType.ECHO
    echo: str

    @classmethod
    def from_json(cls, body_json: dict[Any, Any]) -> BodyEcho:
        echo = body_json.get("echo")
        if not isinstance(echo, str):
            raise BadMessageError(f"Bad echo = {type(echo)} {echo} body_json = {body_json}")
        return BodyEcho(echo=echo)


@dataclass(kw_only=True, frozen=True)
class BodyEchoOk(Body):
    type: MessageType = MessageType.ECHO_OK
    echo: str

    @classmethod
    def from_json(cls, body_json: dict[Any, Any]) -> BodyEchoOk:
        echo = body_json.get("echo")
        if not isinstance(echo, str):
            raise BadMessageError(f"Bad echo = {type(echo)} {echo} body_json = {body_json}")
        return BodyEchoOk(echo=echo)
