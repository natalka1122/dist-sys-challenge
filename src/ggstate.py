class GGState:  # noqa: WPS230
    def __init__(self) -> None:
        self._next_msg_id: int = 0
        self._next_generate_id: int = 0
        self.node_id: str | None = None
        self.node_ids: set[str] = set()
        self._broadcast: set[int] = set()

    @property
    def next_msg_id(self) -> int:
        self._next_msg_id += 1
        return self._next_msg_id

    @property
    def next_generate_id(self) -> str:
        self._next_generate_id += 1
        return f"{self.node_id}_{self._next_generate_id}"

    @property
    def broadcast(self) -> list[int]:
        return list(self._broadcast)

    def add_broadcast_msg(self, msg: int) -> bool:
        current_len = len(self._broadcast)
        self._broadcast.add(msg)
        return len(self._broadcast) != current_len
