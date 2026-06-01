from enum import IntEnum, StrEnum
from typing import Any

DictWithStrKeys = dict[str, Any]


class MessageType(StrEnum):
    ECHO = "echo"
    ECHO_OK = "echo_ok"
    INIT = "init"
    INIT_OK = "init_ok"
    ERROR = "error"
    GENERATE = "generate"
    GENERATE_OK = "generate_ok"
    BROADCAST = "broadcast"
    BROADCAST_OK = "broadcast_ok"
    TOPOLOGY = "topology"
    TOPOLOGY_OK = "topology_ok"
    READ = "read"
    READ_OK = "read_ok"


class ErrorType(IntEnum):
    NOT_SUPPORTED = 10
    CRASH = 13
