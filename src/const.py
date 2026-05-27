from enum import IntEnum, StrEnum


class MessageType(StrEnum):
    ECHO = "echo"
    ECHO_OK = "echo_ok"
    INIT = "init"
    INIT_OK = "init_ok"
    ERROR = "error"
    GENERATE = "generate"
    GENERATE_OK = "generate_ok"


class ErrorType(IntEnum):
    NOT_SUPPORTED = 10
    CRASH = 13
