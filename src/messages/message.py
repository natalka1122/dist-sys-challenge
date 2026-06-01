import json
from dataclasses import dataclass
from typing import Any

from const import DictWithStrKeys, MessageType
from exceptions import BadMessageError
from logging_config import get_logger
from messages.body import Body
from messages.getters import get_dict_with_str_keys, get_int_or_none, get_str

logger = get_logger(__name__)


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
        src = get_str(raw_json, "src")
        dest = get_str(raw_json, "dest")
        body_json: DictWithStrKeys = get_dict_with_str_keys(raw_json, "body")
        body_type_str = get_str(body_json, "type")
        msg_id = get_int_or_none(body_json, "msg_id")
        in_reply_to = get_int_or_none(body_json, "in_reply_to")

        from messages.body_broadcast import BodyBroadcast, BodyBroadcastOk
        from messages.body_echo import BodyEcho, BodyEchoOk
        from messages.body_error import BodyError
        from messages.body_generate import BodyGenerate, BodyGenerateOk
        from messages.body_init import BodyInit, BodyInitOk
        from messages.body_read import BodyRead, BodyReadOk
        from messages.body_topology import BodyTopology, BodyTopologyOk

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
            case MessageType.BROADCAST.value:
                body = BodyBroadcast.from_json(body_json)
            case MessageType.BROADCAST_OK.value:
                body = BodyBroadcastOk.from_json(body_json)
            case MessageType.TOPOLOGY.value:
                body = BodyTopology.from_json(body_json)
            case MessageType.TOPOLOGY_OK.value:
                body = BodyTopologyOk.from_json(body_json)
            case MessageType.READ.value:
                body = BodyRead.from_json(body_json)
            case MessageType.READ_OK.value:
                body = BodyReadOk.from_json(body_json)
            case _:
                raise BadMessageError(
                    f"Not implemented: body_type_str = {body_type_str} raw_json = {raw_json}"
                )
        return Message(src=src, dest=dest, msg_id=msg_id, body=body, in_reply_to=in_reply_to)
