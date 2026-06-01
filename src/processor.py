import asyncio
from types import MappingProxyType
from typing import Mapping, Protocol

from ggstate import GGState
from handlers.broadcast import process_broadcast
from handlers.echo import process_echo
from handlers.error import process_error
from handlers.generate import process_generate
from handlers.init import process_init
from handlers.read import process_read
from handlers.topology import process_topology
from logging_config import get_logger
from messages.body import Body
from messages.body_broadcast import BodyBroadcast
from messages.body_echo import BodyEcho
from messages.body_error import BodyError
from messages.body_generate import BodyGenerate
from messages.body_init import BodyInit
from messages.body_read import BodyRead
from messages.body_topology import BodyTopology
from messages.message import Message
from shutdown import Shutdown

logger = get_logger(__name__)


class ArgsHandler(Protocol):
    def __call__(
        self, body: Body, gg_state: GGState, shutdown_event: asyncio.Event
    ) -> Body | None: ...


HANDLERS: Mapping[type[Body], ArgsHandler] = MappingProxyType(
    {
        BodyBroadcast: process_broadcast,
        BodyEcho: process_echo,
        BodyError: process_error,
        BodyGenerate: process_generate,
        BodyInit: process_init,
        BodyRead: process_read,
        BodyTopology: process_topology,
    }
)


async def processor(
    read_queue: asyncio.Queue[Message],
    write_queue: asyncio.Queue[Message],
    gg_state: GGState,
    shutdown: Shutdown,
) -> None:
    while not shutdown.task.done():
        read_task = asyncio.create_task(read_queue.get())
        await asyncio.wait([shutdown.task, read_task], return_when=asyncio.FIRST_COMPLETED)
        if read_task.done():
            read_data = read_task.result()
            body = read_data.body
            handler = HANDLERS.get(type(body))
            if handler is None:
                continue

            response_body = handler(body=body, gg_state=gg_state, shutdown_event=shutdown.event)
            if response_body is not None:
                message = Message(
                    src=read_data.dest,
                    dest=read_data.src,
                    body=response_body,
                    in_reply_to=read_data.msg_id,
                )
                await write_queue.put(message)
                logger.debug(f"processed {read_data} => {message}")
    logger.info("Stopped processor")
