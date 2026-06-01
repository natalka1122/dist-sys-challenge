from dataclasses import dataclass
from typing import Any

from const import MessageType
from logging_config import get_logger
from messages.body import Body
from messages.getters import get_str

logger = get_logger(__name__)


@dataclass(kw_only=True, frozen=True)
class BodyGenerate(Body):
    type: MessageType = MessageType.GENERATE

    @classmethod
    def from_json(cls, body_json: dict[Any, Any]) -> BodyGenerate:
        return BodyGenerate()


@dataclass(kw_only=True, frozen=True)
class BodyGenerateOk(Body):
    type: MessageType = MessageType.GENERATE_OK
    id: str

    @classmethod
    def from_json(cls, body_json: dict[Any, Any]) -> BodyGenerateOk:
        generated_id = get_str(body_json, "id")
        return BodyGenerateOk(id=generated_id)
