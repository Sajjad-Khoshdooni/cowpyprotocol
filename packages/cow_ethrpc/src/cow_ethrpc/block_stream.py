"""Block stream — port of ethrpc/block_stream."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass

from cow_ethrpc.client import EthRpcClient


@dataclass
class CurrentBlock:
    number: int
    hash: str
    timestamp: int


class BlockStream:
    """Polls for new blocks at a configurable interval."""

    def __init__(self, client: EthRpcClient, poll_interval: float = 1.0) -> None:
        self._client = client
        self._poll_interval = poll_interval
        self._current: CurrentBlock | None = None
        self._subscribers: list[asyncio.Queue[CurrentBlock]] = []

    @property
    def current(self) -> CurrentBlock | None:
        return self._current

    async def start(self) -> None:
        last_number = -1
        while True:
            block = await self._client.get_block("latest")
            number = block["number"]
            if number != last_number:
                self._current = CurrentBlock(
                    number=number,
                    hash=block["hash"].hex(),
                    timestamp=block["timestamp"],
                )
                for q in self._subscribers:
                    await q.put(self._current)
                last_number = number
            await asyncio.sleep(self._poll_interval)

    def subscribe(self) -> asyncio.Queue[CurrentBlock]:
        q: asyncio.Queue[CurrentBlock] = asyncio.Queue()
        self._subscribers.append(q)
        return q

    async def blocks(self) -> AsyncIterator[CurrentBlock]:
        q = self.subscribe()
        while True:
            yield await q.get()
