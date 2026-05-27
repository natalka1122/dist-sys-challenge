# Distributed Systems Challenge — Agent Context

## Project overview

Solutions to the [Fly.io Distributed Systems Challenge](https://fly.io/dist-sys/) (Gossip Glomers), implemented in **Python 3.14 / asyncio**.

Each challenge builds a node process that reads JSON messages from **stdin** and writes JSON replies to **stdout**. Diagnostics go to **stderr**. Maelstrom is the test harness.

## Architecture

```
┌─────────────┐    stdin    ┌──────────────────────┐
│  Maelstrom  │ ──────────▶ │  python3 src/main.py  │
│  (test       │            │                       │
│   harness)  │ ◀────────── │  asyncio event loop   │
└─────────────┘    stdout   └──────────────────────┘
                                │
                            stderr (logging)
```

### Source layout

| File | Role |
|---|---|
| `src/main.py` | Entry point. Sets up signal handlers (SIGINT/SIGTERM → shutdown_event), configures logging, launches `gossip_gloomers_app`. |
| `src/gossip_gloomers_app.py` | Core loop. Three asyncio tasks: `read_json` (stdin → queue), `processor` (queue → reply), `write_json` (queue → stdout). |
| `src/message.py` | Message model. Dataclasses for all body types (`EchoBody`, `EchoOkBody`, `InitBody`, `InitOkBody`, `ErrorBody`) plus `Message` wrapper with JSON serialization. |
| `src/const.py` | Enums: `MessageType` and `ErrorType` (Maelstrom error codes). |
| `src/exceptions.py` | `NeedMoreBytesError` and `BadMessageError`. |
| `src/logging_config.py` | Logging setup (console to stderr + rotating file handler). |

### Data flow

1. `read_json` reads lines from stdin, deserializes JSON into `Message` objects, pushes to `read_queue`
2. `processor` pops from `read_queue`, matches on body type, constructs reply, pushes to `write_queue`
3. `write_json` pops from `write_queue`, serializes to JSON bytes, writes to stdout

### Shutdown

- `main.py` installs signal handlers that set `shutdown_event`
- A single `shutdown_task = asyncio.create_task(shutdown_event.wait())` is shared across all three workers
- Workers check `shutdown_task.done()` each loop iteration
- On shutdown, a 5-second graceful timeout is used, followed by forced cancellation

## Key conventions

- **Strict typing**: mypy `--strict` enforced via `pyproject.toml`. All functions have type annotations.
- **No external deps**: The project has zero runtime dependencies. `pydantic` was removed — all serialization uses `json` + dataclasses.
- **`msg_id` is optional per protocol**: The Maelstrom spec marks `msg_id` as optional. `init_ok` and `error` replies in the spec do not include it.
- **`src`/`dest` swapped on reply**: Currently the processor swaps `src` and `dest` when replying. This works for echo (client↔node) but will need `node_id` awareness for multi-node challenges.
- **Logging to stderr**: Console handler writes to `sys.stderr` to avoid corrupting the stdout protocol stream.

## Running

```bash
# Direct test with a message
echo '{"src":"c0","dest":"n1","body":{"type":"echo","msg_id":1,"echo":"hello"}}' | python3 src/main.py

# Maelstrom test (echo challenge)
maelstrom test -w echo --bin "src/main.py" --node-count 1 --time-limit 10 --rate 1 --log-stderr
```

## Current status

Working on **Challenge #1: Echo**. The echo handler is complete: receives `echo`, replies `echo_ok`. Init handshake is also handled.

## Known gaps (deferred to later challenges)

1. **`msg_id` for outgoing messages** — no monotonic counter yet. Not needed for echo.
2. **Node identity** — `InitBody` doesn't store `node_id` / `node_ids`. Needed for multi-node.
3. **`src` awareness** — processor blindly swaps src/dest instead of setting its own node_id.
4. **Unit tests** — no tests yet. Only end-to-end via Maelstrom.

## Tech

- Python 3.14, asyncio
- mypy `--strict`, ruff (wemake-python-styleguide)
- Maelstrom v0.2.4 (in dev container)