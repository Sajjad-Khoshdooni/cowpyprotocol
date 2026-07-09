"""Auction run loop — port of autopilot auction cutting."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from cow_ethrpc import BlockStream, EthRpcClient
from cow_solver import select_winner
from cow_solver.dto import Solution

logger = logging.getLogger(__name__)


class AuctionRunLoop:
    """Cuts auctions on every new block."""

    def __init__(self, client: EthRpcClient, db: Any) -> None:
        self._client = client
        self._db = db
        self._block_stream = BlockStream(client)
        self._auction_id = 0
        self._solutions: list[Solution] = []

    async def run(self) -> None:
        logger.info("starting auction run loop")
        asyncio.create_task(self._block_stream.start())
        async for block in self._block_stream.blocks():
            await self._cut_auction(block.number)

    async def _cut_auction(self, block_number: int) -> None:
        self._auction_id += 1
        logger.info("cutting auction %d at block %d", self._auction_id, block_number)
        # Fetch eligible orders, apply fee policies, store auction
        winner = select_winner(self._solutions)
        if winner:
            logger.info("winner: %s (score=%.2f)", winner.solver, winner.score)
        self._solutions.clear()

    async def submit_solution(self, solution: Solution) -> None:
        self._solutions.append(solution)
