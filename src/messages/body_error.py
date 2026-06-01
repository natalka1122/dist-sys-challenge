from dataclasses import dataclass
from typing import Any

from const import ErrorType, MessageType
from logging_config import get_logger
from messages.body import Body
from messages.func import get_int, get_str

logger = get_logger(__name__)


@dataclass(kw_only=True, frozen=True)
class BodyError(Body):
    type: MessageType = MessageType.ERROR
    text: str
    code: ErrorType

    @classmethod
    def from_json(cls, body_json: dict[Any, Any]) -> BodyError:
        text = get_str(body_json, "text")
        code = ErrorType(get_int(body_json, "code"))
        return BodyError(text=text, code=code)
