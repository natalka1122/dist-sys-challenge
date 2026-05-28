import asyncio


class Shutdown:
    def __init__(self, event: asyncio.Event) -> None:
        self._event = event
        self._task = asyncio.create_task(self.event.wait())

    @property
    def event(self) -> asyncio.Event:
        return self._event

    @property
    def task(self) -> asyncio.Task[bool]:
        return self._task
