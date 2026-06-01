# Distributed Systems Challenge — Agent Context

> **Learning project**: The human is writing the code. Do not give too much information unless asked specifically. Keep responses concise and focused on what was asked.

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
| `src/main.py` | Entry point. Sets up signal handlers, configures logging, launches `gossip_gloomers_app`. |
| `src/gossip_gloomers_app.py` | Core loop. Three asyncio tasks: `read_json` (stdin → queue), `processor` (queue → reply), `write_json` (queue → stdout). |
| `src/processor.py` | Handler dispatch. Maps body types to handler functions via `HANDLERS` registry. |
| `src/handlers/` | Business logic handlers (echo, init, generate, broadcast, read, topology, error). |
| `src/messages/` | Message models. `messages/body.py` (base `Body` class), `messages/message.py` (wrapper with JSON serialization), plus per-type body modules. |
| `src/ggstate.py` | Shared node state — `node_id`, `node_ids`, `next_msg_id` counter, `next_generate_id` counter. |
| `src/const.py` | Enums: `MessageType` and `ErrorType` (Maelstrom error codes). |
| `src/exceptions.py` | `NeedMoreBytesError` and `BadMessageError`. |
| `src/logging_config.py` | Logging setup (console to stderr + rotating file handler). |
| `src/shutdown.py` | `Shutdown` wrapper around `asyncio.Event` for task coordination. |

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

# Single-Node Broadcast challenge (3a)
maelstrom test -w broadcast --bin "src/main.py" --node-count 1 --time-limit 20 --rate 10 --log-stderr

# Multi-Node Broadcast challenge (3b)
maelstrom test -w broadcast --bin "src/main.py" --node-count 3 --time-limit 20 --rate 10 --log-stderr
```

## Current status

- ✅ **Challenge #1 — Echo**: Completed and passing.
- ✅ **Challenge #2 — Unique ID Generation**: Completed and passing. Generates globally unique IDs (`{node_id}_{counter}`).
- ✅ **Challenge #3a — Single-Node Broadcast**: Completed and passing. Stores messages in `GGState.broadcast`, replies `broadcast_ok` and `read_ok`. 210 ops, 0 lost/duplicated/stale, `:valid? true`.
- ⏳ **Challenge #3b — Multi-Node Broadcast**: Next up. Need to broadcast to all nodes via `node_ids`.
- ⏳ **Challenge #3c–3e**: Not started.

**Maelstrom test results**

- **Echo** (2026-05-27): passing.
- **unique-ids** (2026-05-27): 14,544 operations, 0 duplicates, `:valid? true`.
- **broadcast (3a)** (2026-05-28): 210 operations, 115/115 broadcast ok, 95/95 read ok, 0 lost/duplicated/stale, `:valid? true`.

## Issues

| # | Title | Status |
|---|-------|--------|
| [1](https://github.com/natalka1122/dist-sys-challenge/issues/1) | Add monotonic msg_id generation | ✅ Closed |
| [2](https://github.com/natalka1122/dist-sys-challenge/issues/2) | Globally unique ID generation | ✅ Closed |
| [3](https://github.com/natalka1122/dist-sys-challenge/issues/3) | Store node_id / node_ids from init message | ✅ Closed |
| [4](https://github.com/natalka1122/dist-sys-challenge/issues/4) | Add unit and integration tests | Open |
| [5](https://github.com/natalka1122/dist-sys-challenge/issues/5) | Decouple growing files into smaller modules | ✅ Closed |
| [6](https://github.com/natalka1122/dist-sys-challenge/issues/6) | Return proper Maelstrom error instead of crashing on unknown types | Open |
| [7](https://github.com/natalka1122/dist-sys-challenge/issues/7) | Reduce logging verbosity | ✅ Closed |
| [9](https://github.com/natalka1122/dist-sys-challenge/issues/9) | Implement Challenge #3a: Single-Node Broadcast | ✅ Closed |
| [10](https://github.com/natalka1122/dist-sys-challenge/issues/10) | Implement Challenge #3b: Multi-Node Broadcast | Open |
| [11](https://github.com/natalka1122/dist-sys-challenge/issues/11) | Implement Challenge #3d: Efficient Broadcast, Part I | Open |
| [12](https://github.com/natalka1122/dist-sys-challenge/issues/12) | Implement Challenge #3c: Fault Tolerant Broadcast | Open |
| [13](https://github.com/natalka1122/dist-sys-challenge/issues/13) | Implement Challenge #3e: Efficient Broadcast, Part II | Open |

## Challenge breakdown

The challenges are split into sub-challenges (a, b, c, ...):

| # | Name | URL | Status |
|---|------|-----|--------|
| 1 | Echo | [/dist-sys/1](https://fly.io/dist-sys/1/) |
| 2 | Unique ID Generation | [/dist-sys/2](https://fly.io/dist-sys/2/) |
| 3a | Single-Node Broadcast | [/dist-sys/3a](https://fly.io/dist-sys/3a/) | ✅ Done |
| 3b | Multi-Node Broadcast | [/dist-sys/3b](https://fly.io/dist-sys/3b/) | ⏳ Not started |
| 3c | Fault Tolerant Broadcast | [/dist-sys/3c](https://fly.io/dist-sys/3c/) | ⏳ Not started |
| 3d | Efficient Broadcast, Part I | [/dist-sys/3d](https://fly.io/dist-sys/3d/) | ⏳ Not started |
| 3e | Efficient Broadcast, Part II | [/dist-sys/3e](https://fly.io/dist-sys/3e/) | ⏳ Not started |
| 4 | Grow-Only Counter | [/dist-sys/4](https://fly.io/dist-sys/4/) | ⏳ Not started |
| 5a | Single-Node Kafka-Style Log | [/dist-sys/5a](https://fly.io/dist-sys/5a/) | ⏳ Not started |
| 5b | Multi-Node Kafka-Style Log | [/dist-sys/5b](https://fly.io/dist-sys/5b/) | ⏳ Not started |
| 5c | Efficient Kafka-Style Log | [/dist-sys/5c](https://fly.io/dist-sys/5c/) | ⏳ Not started |
| 6a | Single-Node, Totally-Available Transactions | [/dist-sys/6a](https://fly.io/dist-sys/6a/) | ⏳ Not started |
| 6b | Totally-Available, Read Uncommitted Transactions | [/dist-sys/6b](https://fly.io/dist-sys/6b/) | ⏳ Not started |
| 6c | Totally-Available, Read Committed Transactions | [/dist-sys/6c](https://fly.io/dist-sys/6c/) | ⏳ Not started |

## Known gaps

1. **Unit tests** — no tests yet. Only end-to-end via Maelstrom.
2. **`src`/`dest` swapping** — processor blindly swaps `src`/`dest` instead of using `gg_state.node_id`. Works for single-node echo/generate, needs fixing for multi-node challenges (3b+).
3. **Fire-and-forget messaging** — 3a+ needs ability to send messages without expecting a reply (gossip to neighbors).
4. **Message routing** — currently only replies. 3b+ needs ability to send to specific nodes via `node_ids`.

## Tech

- Python 3.14, asyncio
- mypy `--strict`, ruff (wemake-python-styleguide)
- Maelstrom v0.2.4 (in dev container)