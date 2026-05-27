# Distributed Systems Challenge in Python

Solutions to the [Fly.io Distributed Systems Challenge](https://fly.io/dist-sys/) (a.k.a. "Gossip Glomers"), implemented in **Python 3.14 / asyncio**.

## Status

Currently working through **Challenge #3a: Single-Node Broadcast** ([spec](https://fly.io/dist-sys/3a/)).

- ✅ **Challenge #1 — Echo**: Completed and passing.
- ✅ **Challenge #2 — Unique ID Generation**: Completed and passing. Generates globally unique IDs (`{node_id}_{counter}`).
- 🚧 **Challenge #3a — Single-Node Broadcast**: Starting next.

| # | Challenge | URL | Status |
|---|-----------|-----|--------|
| 1 | Echo | [/dist-sys/1](https://fly.io/dist-sys/1/) | ✅ Done |
| 2 | Unique ID Generation | [/dist-sys/2](https://fly.io/dist-sys/2/) | ✅ Done |
| 3a | Single-Node Broadcast | [/dist-sys/3a](https://fly.io/dist-sys/3a/) | 🚧 In progress |
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

## What is this?

[Gossip Glomers](https://fly.io/dist-sys/) is a series of distributed systems challenges created by [Kyle Kingsbury](https://aphyr.com/) (author of Jepsen). Participants build a node that communicates over **stdin/stdout** using [Maelstrom](https://github.com/jepsen-io/maelstrom), a Jepsen-based test harness. Each challenge introduces a new distributed systems concept — RPC, broadcast, fault tolerance, linearizability, etc.

The test harness sends JSON messages to the node's stdin, and the node replies on stdout. The harness then verifies correctness properties (e.g. "all nodes eventually receive the message").

## Stack

- **Language:** Python 3.14
- **Async runtime:** `asyncio` (stdin/stdout streams)
- **Type checking:** mypy (`--strict`)
- **Linting:** flake8 + wemake-python-styleguide
- **Dev container:** Ubuntu 24.04 with Maelstrom v0.2.4 pre-installed

## Project structure

```
├── src/
│   ├── __init__.py         # Package marker
│   ├── main.py             # Entry point — signal handling, asyncio runner
│   ├── gossip_gloomers_app.py    # Core loop: stdin reader, processor, stdout writer
│   ├── ggstate.py          # Shared node state (node_id, counters, generation)
│   ├── message.py          # Message model (JSON deserialization)
│   ├── const.py            # Message type enum
│   ├── exceptions.py       # Custom exceptions
│   └── logging_config.py   # Logging setup (console + rotating file)
├── .devcontainer/          # Dev container config + Maelstrom install
├── pyproject.toml          # Python project metadata
├── .flake8                 # Flake8 configuration
├── .gitignore
└── README.md
```

All source code lives under `src/`. Run via:

```bash
python3 src/main.py
```

## Running

### Inside the dev container (recommended)

```bash
# Build & launch the dev container (VS Code: Reopen in Container)
# Then run the node directly with a message:
cd /workspaces/dist-sys-challenge

# Echo test
echo '{"src":"c0","dest":"n1","body":{"type":"echo","msg_id":1,"echo":"hello"}}' | python3 src/main.py

# Unique ID generation test
echo '{"src":"c0","dest":"n1","body":{"type":"generate","msg_id":1}}' | python3 src/main.py
```

### With Maelstrom (full test suite)

```bash
cd /workspaces/dist-sys-challenge

# Echo challenge
maelstrom test \
  -w echo \
  --bin "src/main.py" \
  --node-count 1 \
  --time-limit 10 \
  --rate 1 \
  --log-stderr

# Unique ID Generation challenge
maelstrom test \
  -w unique-ids \
  --bin "src/main.py" \
  --time-limit 30 \
  --rate 1000 \
  --node-count 3 \
  --availability total \
  --nemesis partition \
  --log-stderr

# Single-Node Broadcast challenge (3a)
maelstrom test \
  -w broadcast \
  --bin "src/main.py" \
  --node-count 1 \
  --time-limit 20 \
  --rate 10 \
  --log-stderr
```

> ⚠️ Tests require Maelstrom (included in the dev container). For manual install see [maelstrom/releases](https://github.com/jepsen-io/maelstrom/releases).

## Dev container setup

The `.devcontainer/` mounts several host paths into the container via `localEnv` variables.
Set these in your shell rc file (e.g. `~/.bashrc`) before launching the container:

```bash
# Host paths for bind mounts (WSL paths, e.g. /mnt/c/Users/...)
export HOST_SSH_DIR="/mnt/c/Users/YourName/.ssh"
export HOST_GH_CONFIG_DIR="$HOME/.config/gh_<project-name>"

# Git identity (required by post_start_command.sh)
export GIT_AUTHOR_EMAIL="your-email@example.com"
export GIT_AUTHOR_NAME="Your Name"

# API key for the pi coding agent
export MY_OPENROUTER_API_KEY="sk-or-v1-..."
```

> The PI agent dir is auto-resolved to `${localWorkspaceFolder}/.pi/agent` — no env var needed.

## Tests

There are currently **no unit tests**. The project is tested end-to-end via Maelstrom's test harness (see [Running](#running)). Adding tests is a known gap.

## License

MIT