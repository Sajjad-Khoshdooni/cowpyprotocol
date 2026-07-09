"""Solana settlement indexer via Yellowstone gRPC."""

from __future__ import annotations

import asyncio
import logging

logger = logging.getLogger(__name__)


class SolanaIndexer:
    """Indexes Solana settlement events via Yellowstone gRPC."""

    def __init__(self, grpc_url: str, db_url: str) -> None:
        self._grpc_url = grpc_url
        self._db_url = db_url

    async def run(self) -> None:
        logger.info("starting solana indexer (grpc=%s)", self._grpc_url)
        while True:
            await self._index_blocks()
            await asyncio.sleep(1)

    async def _index_blocks(self) -> None:
        logger.debug("polling solana blocks via yellowstone gRPC")
        # Yellowstone gRPC client integration placeholder
