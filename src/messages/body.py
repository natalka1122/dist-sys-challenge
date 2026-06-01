from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass

from const import DictWithStrKeys, MessageType
from logging_config import get_logger

logger = get_logger(__name__)


@dataclass(kw_only=True, frozen=True)
class Body(ABC):
    type: MessageType

    def to_json(self) -> DictWithStrKeys:
        result: DictWithStrKeys = {"type": self.type.value}
        for key, value in asdict(self).items():
            if key != "type":
                result[key] = value
        return result

    @classmethod
    @abstractmethod
    def from_json(cls, body_json: DictWithStrKeys) -> "Body": ...
