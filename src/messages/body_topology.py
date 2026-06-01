from dataclasses import dataclass
from typing import Any

from const import DictWithStrKeys, MessageType
from logging_config import get_logger
from messages.body import Body
from messages.func import get_dict_with_str_keys

logger = get_logger(__name__)


@dataclass(kw_only=True, frozen=True)
class BodyTopology(Body):
    type: MessageType = MessageType.TOPOLOGY
    topology: DictWithStrKeys

    @classmethod
    def from_json(cls, body_json: dict[Any, Any]) -> BodyTopology:
        topology = get_dict_with_str_keys(body_json, "topology")
        return BodyTopology(topology=topology)


@dataclass(kw_only=True, frozen=True)
class BodyTopologyOk(Body):
    type: MessageType = MessageType.TOPOLOGY_OK

    @classmethod
    def from_json(cls, body_json: dict[Any, Any]) -> BodyTopologyOk:
        return BodyTopologyOk()
