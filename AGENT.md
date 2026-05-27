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
| `src/message.py` | Message model. Dataclasses for all body types (`EchoBody`, `EchoOkBody`, `InitBody`, `InitOkBody`, `ErrorBody`, `BodyGenerate`, `BodyGenerateOk`) plus `Message` wrapper with JSON serialization. |
| `src/ggstate.py` | Shared node state — `node_id`, `node_ids`, `next_msg_id` counter, `next_generate_id` counter. |
| `src/const.py` | Enums: `MessageType` and `ErrorType` (Maelstrom error codes). |
| `src/exceptions.py` | `NeedMoreBytesError` and `BadMessageError`. |
| `src/logging_config.py` | Logging setup (console to stderr + rotating file handler). |

### Data flow

1. `read_json` reads lines from stdin, deserializes JSON into `Message` objects, pushes to `read_queue`
2. `processor` pops from `read_queue`, matches on body type, constructs reply (using `GGState` for node identity), pushes to `write_queue`
3. `write_json` pops from `write_queue`, assigns `msg_id` from `GGState.next_msg_id`, serializes to JSON bytes, writes to stdout

### Shutdown

- `main.py` installs signal handlers that set `shutdown_event`
- A single `shutdown_task = asyncio.create_task(shutdown_event.wait())` is shared across all three workers
- Workers check `shutdown_task.done()` each loop iteration
- On shutdown, a 5-second graceful timeout is used, followed by forced cancellation

## Key conventions

- **Strict typing**: mypy `--strict` enforced via `pyproject.toml`. All functions have type annotations.
- **No external deps**: The project has zero runtime dependencies. `pydantic` was removed — all serialization uses `json` + dataclasses.
- **`msg_id` is assigned at write time**: `write_json` assigns a monotonic `msg_id` from `GGState.next_msg_id` before serialization. The Maelstrom spec marks `msg_id` as optional, but outgoing messages carry it.
- **`src`/`dest` swapped on reply**: Currently the processor swaps `src` and `dest` when replying. This works for echo (client↔node) but will need `node_id` awareness for multi-node challenges.
- **Node identity stored in GGState**: `node_id` and `node_ids` are captured from the `init` message and stored in shared state.
- **Unique IDs via node_id + counter**: `GGState.next_generate_id` produces `{node_id}_{counter}` strings (e.g. `"n0_1"`).
- **Logging to stderr**: Console handler writes to `sys.stderr` to avoid corrupting the stdout protocol stream.

## Running

```bash
# Direct test with a message (echo)
echo '{"src":"c0","dest":"n1","body":{"type":"echo","msg_id":1,"echo":"hello"}}' | python3 src/main.py

# Direct test (generate)
echo '{"src":"c0","dest":"n1","body":{"type":"generate","msg_id":1}}' | python3 src/main.py

# Maelstrom test (echo challenge)
maelstrom test -w echo --bin "src/main.py" --node-count 1 --time-limit 10 --rate 1 --log-stderr

# Maelstrom test (unique-ids challenge)
maelstrom test -w unique-ids --bin "src/main.py" --time-limit 30 --rate 1000 --node-count 3 --availability total --nemesis partition --log-stderr
```

## Current status

- ✅ **Challenge #1 — Echo**: Completed and passing (init handshake + echo_ok reply).
- ✅ **Issues #1–3**: `msg_id` generation, unique ID generation, and node identity storage — all implemented and closed.
- 🚧 **Challenge #2 — Unique ID Generation**: Implemented (unique IDs via `{node_id}_{counter}`). CI pipeline has formatting issues to fix first, then re-run the unique-ids Maelstrom test.

**Last test result** (2026-05-27, pre-fix): 19,121 operations, all returned `id=1`. Duplicate count = 19,121. `:valid? false`.

## Issues

| # | Title | Status |
|---|-------|--------|
| [1](https://github.com/natalka1122/dist-sys-challenge/issues/1) | Add monotonic msg_id generation | ✅ Closed |
| [2](https://github.com/natalka1122/dist-sys-challenge/issues/2) | Globally unique ID generation (replace hardcoded id=1) | ✅ Closed |
| [3](https://github.com/natalka1122/dist-sys-challenge/issues/3) | Store node_id / node_ids from init message | ✅ Closed |
| [4](https://github.com/natalka1122/dist-sys-challenge/issues/4) | Add unit and integration tests | Open |
| [5](https://github.com/natalka1122/dist-sys-challenge/issues/5) | Decouple growing files into smaller modules | Open |
| [6](https://github.com/natalka1122/dist-sys-challenge/issues/6) | Return proper Maelstrom error instead of crashing on unknown types | Open |
| [7](https://github.com/natalka1122/dist-sys-challenge/issues/7) | Reduce logging verbosity | Open |

## Known gaps

1. **Unit tests** — no tests yet. Only end-to-end via Maelstrom.
2. **Handler dispatch** — still uses `if/elif` chain in `processor()`. Will need a registry pattern as more body types are added.
3. **`src`/`dest` swapping** — processor blindly swaps src/dest instead of using `gg_state.node_id`. Works for single-node echo/generate, needs fixing for multi-node challenges.

## Tech

- Python 3.14, asyncio
- mypy `--strict`, ruff (wemake-python-styleguide)
- Maelstrom v0.2.4 (in dev container)