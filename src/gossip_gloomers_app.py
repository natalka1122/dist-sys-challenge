import asyncio
import json
import sys

from exceptions import BadMessageError
from ggstate import GGState
from logging_config import get_logger
from messages.body_broadcast import (
    BodyBroadcast,
    BodyBroadcastOk,
)
from messages.body_echo import BodyEcho, BodyEchoOk
from messages.body_generate import BodyGenerate, BodyGenerateOk
from messages.body_init import BodyInit, BodyInitOk
from messages.body_read import (
    BodyRead,
    BodyReadOk,
)
from messages.body_topology import (
    BodyTopology,
    BodyTopologyOk,
)
from messages.message import Message
from shutdown import Shutdown

logger = get_logger(__name__)


async def connect_stdin_stdout() -> (  # noqa: WPS210
    tuple[asyncio.StreamReader, asyncio.StreamWriter]
):
    loop = asyncio.get_running_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    w_transport, w_protocol = await loop.connect_write_pipe(
        asyncio.streams.FlowControlMixin, sys.stdout
    )
    writer = asyncio.StreamWriter(w_transport, w_protocol, reader, loop)
    return reader, writer


async def read_json(
    reader: asyncio.StreamReader,
    read_queue: asyncio.Queue[Message],
    shutdown: Shutdown,
) -> None:
    while not shutdown.task.done():
        read_task = asyncio.create_task(reader.readline())
        await asyncio.wait([shutdown.task, read_task], return_when=asyncio.FIRST_COMPLETED)
        if read_task.done():
            result = read_task.result()
            try:
                message = Message.from_bytes(result)
            except BadMessageError as exc:
                logger.error(f"Got {result!r}, bad message, {exc}")
                shutdown.event.set()
                break
            logger.debug(f"message = {message.to_json()}")
            await read_queue.put(message)
    logger.info("Stopped read_json")


async def write_json(
    writer: asyncio.StreamWriter,
    write_queue: asyncio.Queue[Message],
    gg_state: GGState,
    shutdown: Shutdown,
) -> None:
    while not shutdown.task.done():
        next_item_task = asyncio.create_task(write_queue.get())
        await asyncio.wait([shutdown.task, next_item_task], return_when=asyncio.FIRST_COMPLETED)
        if next_item_task.done():
            next_item = next_item_task.result()
            next_item.msg_id = gg_state.next_msg_id
            next_item_bytes = json.dumps(next_item.to_json()).encode()
            writer.write(next_item_bytes)
            writer.write(b"\n")
            writer_drain_task = asyncio.create_task(writer.drain())
            await asyncio.wait(
                [shutdown.task, writer_drain_task], return_when=asyncio.FIRST_COMPLETED
            )
            logger.debug(f"write {next_item}")
    logger.info("Stopped write_json")


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
            if isinstance(body, BodyEcho):
                body = BodyEchoOk(echo=body.echo)
            elif isinstance(body, BodyInit):
                if isinstance(gg_state.node_id, str):
                    logger.error(f"Got init but already have node_id. body = {body}")
                    shutdown.event.set()
                    break
                gg_state.node_id = body.node_id
                gg_state.node_ids = set(body.node_ids)
                body = BodyInitOk()
            elif isinstance(body, BodyTopology):
                body = BodyTopologyOk()
            elif isinstance(body, BodyGenerate):
                body = BodyGenerateOk(id=gg_state.next_generate_id)
            elif isinstance(body, BodyBroadcast):
                gg_state.broadcast.add(body.message)
                body = BodyBroadcastOk()
            elif isinstance(body, BodyRead):
                body = BodyReadOk(messages=list(gg_state.broadcast))
            else:
                logger.error(f"Got unknown body = {body}")
                shutdown.event.set()
                break
            message = Message(
                src=read_data.dest, dest=read_data.src, body=body, in_reply_to=read_data.msg_id
            )
            await write_queue.put(message)
            logger.debug(f"processed {read_data} => {message}")
    logger.info("Stopped processor")


async def gossip_gloomers_app(
    shutdown_event: asyncio.Event,
) -> None:
    gg_state = GGState()
    reader, writer = await connect_stdin_stdout()
    read_queue: asyncio.Queue[Message] = asyncio.Queue()
    write_queue: asyncio.Queue[Message] = asyncio.Queue()
    shutdown = Shutdown(shutdown_event)
    tasks: list[asyncio.Task[None]] = [
        asyncio.create_task(
            read_json(
                reader,
                read_queue=read_queue,
                shutdown=shutdown,
            )
        ),
        asyncio.create_task(
            write_json(
                writer,
                write_queue=write_queue,
                gg_state=gg_state,
                shutdown=shutdown,
            )
        ),
        asyncio.create_task(
            processor(
                read_queue=read_queue,
                write_queue=write_queue,
                gg_state=gg_state,
                shutdown=shutdown,
            )
        ),
    ]
    logger.info("Everybody started")
    await shutdown_event.wait()
    logger.info("Shutdown signal received, stopping workers...")

    try:
        await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=5)
    except asyncio.TimeoutError:
        logger.warning("Some tasks did not finish in time, forcing exit...")
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)  # wait for cancellation to complete
    logger.info("All workers stopped. Goodbye!")
