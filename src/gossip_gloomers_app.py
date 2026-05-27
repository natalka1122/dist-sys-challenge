import asyncio
import json
import sys

from exceptions import BadMessageError
from logging_config import get_logger
from message import BodyEcho, BodyEchoOk, BodyInit, BodyInitOk, Message

logger = get_logger(__name__)


async def connect_stdin_stdout() -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:  # noqa: WPS210
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
    shutdown_event: asyncio.Event,
    shutdown_task: asyncio.Task[bool],
) -> None:
    while not shutdown_task.done():
        read_task = asyncio.create_task(reader.readline())
        await asyncio.wait([shutdown_task, read_task], return_when=asyncio.FIRST_COMPLETED)
        if read_task.done():
            result = read_task.result()
            try:
                message = Message.from_bytes(result)
            except BadMessageError as exc:
                logger.error(f"Got {result!r}, bad message, {exc}")
                shutdown_event.set()
            else:
                logger.debug(f"message = {message.to_json()}")
                await read_queue.put(message)
    logger.info("Stopped read_json")


async def write_json(
    writer: asyncio.StreamWriter,
    write_queue: asyncio.Queue[Message],
    shutdown_event: asyncio.Event,
    shutdown_task: asyncio.Task[bool],
) -> None:
    while not shutdown_task.done():
        next_item_task = asyncio.create_task(write_queue.get())
        await asyncio.wait([shutdown_task, next_item_task], return_when=asyncio.FIRST_COMPLETED)
        if next_item_task.done():
            next_item = next_item_task.result()
            next_item_bytes = json.dumps(next_item.to_json()).encode()
            writer.write(next_item_bytes)
            writer.write(b"\n")
            writer_drain_task = asyncio.create_task(writer.drain())
            await asyncio.wait(
                [shutdown_task, writer_drain_task], return_when=asyncio.FIRST_COMPLETED
            )
            logger.info(f"write {next_item}")
    logger.info("Stopped write_json")


async def processor(
    read_queue: asyncio.Queue[Message],
    write_queue: asyncio.Queue[Message],
    shutdown_event: asyncio.Event,
    shutdown_task: asyncio.Task[bool],
) -> None:
    while not shutdown_task.done():
        read_task = asyncio.create_task(read_queue.get())
        await asyncio.wait([shutdown_task, read_task], return_when=asyncio.FIRST_COMPLETED)
        if read_task.done():
            read_data = read_task.result()
            body = read_data.body
            if isinstance(body, BodyEcho):
                body = BodyEchoOk(echo=body.echo)
            elif isinstance(body, BodyInit):
                body = BodyInitOk()
            else:
                shutdown_event.set()
                break
            message = Message(
                src=read_data.dest, dest=read_data.src, body=body, in_reply_to=read_data.msg_id
            )
            await write_queue.put(message)
            logger.info(f"processed {read_data} => {message}")
    logger.info("Stopped processor")


async def gossip_gloomers_app(
    shutdown_event: asyncio.Event,
) -> None:
    reader, writer = await connect_stdin_stdout()
    read_queue: asyncio.Queue[Message] = asyncio.Queue()
    write_queue: asyncio.Queue[Message] = asyncio.Queue()
    shutdown_task: asyncio.Task[bool] = asyncio.create_task(shutdown_event.wait())
    tasks: list[asyncio.Task[None]] = [
        asyncio.create_task(
            read_json(
                reader,
                read_queue=read_queue,
                shutdown_event=shutdown_event,
                shutdown_task=shutdown_task,
            )
        ),
        asyncio.create_task(
            write_json(
                writer,
                write_queue=write_queue,
                shutdown_event=shutdown_event,
                shutdown_task=shutdown_task,
            )
        ),
        asyncio.create_task(
            processor(
                read_queue=read_queue,
                write_queue=write_queue,
                shutdown_event=shutdown_event,
                shutdown_task=shutdown_task,
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
