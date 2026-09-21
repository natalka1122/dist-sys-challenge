class Broadcast:
    def __init__(self) -> None:
        self._numbers: dict[int, dict[str, set[int]]] = {}  # noqa: WPS234
