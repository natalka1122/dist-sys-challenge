import json
from abc import abstractmethod
from dataclasses import asdict, dataclass
from typing import Any, cast

from const import ErrorType, MessageType
from exceptions import BadMessageError
from logging_config import get_logger

logger = get_logger(__name__)

DictWithStrKeys = dict[str, Any]


def _get_str(raw_json: dict[Any, Any], key: str) -> str:
    result = raw_json.get(key)
    if not isinstance(result, str):
        raise BadMessageError(f"Wrong {key} = {type(result)} {result} raw_json = {raw_json}")
    return result


def _get_int_or_none(raw_json: dict[Any, Any], key: str) -> int | None:
    result = raw_json.get(key)
    if result is not None and not isinstance(result, int):
        raise BadMessageError(f"Wrong {key} = {type(result)} {result} raw_json = {raw_json}")
    return result


def _get_int(raw_json: dict[Any, Any], key: str) -> int:
    result = raw_json.get(key)
    if not isinstance(result, int):
        raise BadMessageError(f"Wrong {key} = {type(result)} {result} raw_json = {raw_json}")
    return result


def _get_dict_with_str_keys(raw_json: dict[Any, Any], key: str) -> DictWithStrKeys:
    result = raw_json.get(key)
    if not isinstance(result, dict):
        raise BadMessageError(f"Wrong {key} = {type(result)} {result} result = {raw_json}")
    result = cast(DictWithStrKeys, result)
    if not all(isinstance(k, str) for k in result):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise BadMessageError(f"Wrong {key} = {type(result)} {result} result = {raw_json}")
    return result


@dataclass(kw_only=True, frozen=True)
class Body:
    type: MessageType

    def to_json(self) -> DictWithStrKeys:
        result: DictWithStrKeys = {"type": self.type.value}
        for key, value in asdict(self).items():
            if key != "type":
                result[key] = value
        return result

    @classmethod
    @abstractmethod
    def from_json(cls, body_json: dict[Any, Any]) -> "Body": ...


@dataclass(kw_only=True, frozen=True)
class BodyInit(Body):
    type: MessageType = MessageType.INIT
    node_id: str
    node_ids: list[str]

    @classmethod
    def from_json(cls, body_json: dict[Any, Any]) -> BodyInit:
        node_id = body_json.get("node_id")
        if not isinstance(node_id, str):
            raise BadMessageError(
                f"Bad node_id = {type(node_id)} {node_id} body_json = {body_json}"
            )
        node_ids = body_json.get("node_ids")
        if not isinstance(node_ids, list):
            raise BadMessageError(
                f"Bad node_ids = {type(node_ids)} {node_ids} body_json = {body_json}"
            )
        node_ids = cast(list[str], node_ids)
        if not all(isinstance(k, str) for k in node_ids):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise BadMessageError(f"Wrong node_ids = {node_ids} body_json = {body_json}")
        return BodyInit(node_id=node_id, node_ids=node_ids)


@dataclass(kw_only=True, frozen=True)
class BodyInitOk(Body):
    type: MessageType = MessageType.INIT_OK

    @classmethod
    def from_json(cls, body_json: dict[Any, Any]) -> BodyInitOk:
        return BodyInitOk()


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


@dataclass(kw_only=True, frozen=True)
class BodyError(Body):
    type: MessageType = MessageType.ERROR
    text: str
    code: ErrorType

    @classmethod
    def from_json(cls, body_json: dict[Any, Any]) -> BodyError:
        text = _get_str(body_json, "text")
        code = ErrorType(_get_int(body_json, "code"))
        return BodyError(text=text, code=code)


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
        generated_id = _get_str(body_json, "id")
        return BodyGenerateOk(id=generated_id)


@dataclass(kw_only=True)
class Message:
    src: str
    dest: str
    body: Body
    msg_id: int | None = None
    in_reply_to: int | None = None

    def to_json(self) -> dict[str, Any]:
        result: dict[str, Any] = {"src": self.src, "dest": self.dest}
        body: dict[str, Any] = self.body.to_json()
        if self.msg_id is not None:
            body["msg_id"] = self.msg_id
        if self.in_reply_to is not None:
            body["in_reply_to"] = self.in_reply_to
        result["body"] = body
        return result

    @classmethod
    def from_bytes(cls, raw_bytes: bytes) -> Message:
        try:
            raw_json = json.loads(raw_bytes)
        except json.JSONDecodeError:
            raise BadMessageError(f"Malformed raw_bytes = {raw_bytes!r}")
        src = _get_str(raw_json, "src")
        dest = _get_str(raw_json, "dest")
        body_json: DictWithStrKeys = _get_dict_with_str_keys(raw_json, "body")
        body_type_str = _get_str(body_json, "type")
        msg_id = _get_int_or_none(body_json, "msg_id")
        in_reply_to = _get_int_or_none(body_json, "in_reply_to")

        body: Body
        match body_type_str:
            case MessageType.ECHO.value:
                body = BodyEcho.from_json(body_json)
            case MessageType.ECHO_OK.value:
                body = BodyEchoOk.from_json(body_json)
            case MessageType.INIT.value:
                body = BodyInit.from_json(body_json)
            case MessageType.INIT_OK.value:
                body = BodyInitOk.from_json(body_json)
            case MessageType.ERROR.value:
                body = BodyError.from_json(body_json)
            case MessageType.GENERATE.value:
                body = BodyGenerate.from_json(body_json)
            case MessageType.GENERATE_OK.value:
                body = BodyGenerateOk.from_json(body_json)
            case _:
                raise BadMessageError(
                    f"Not implemented: body_type_str = {body_type_str} raw_json = {raw_json}"
                )
        return Message(src=src, dest=dest, msg_id=msg_id, body=body, in_reply_to=in_reply_to)
