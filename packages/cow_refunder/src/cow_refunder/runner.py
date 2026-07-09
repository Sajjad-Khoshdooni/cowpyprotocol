"""EthFlow refund runner."""

from __future__ import annotations

import asyncio
import logging

from cow_ethrpc import EthRpcClient

logger = logging.getLogger(__name__)


class RefunderRunner:
    """Processes expired EthFlow orders and refunds ETH."""

    def __init__(self, client: EthRpcClient, db_url: str, interval: int = 60) -> None:
        self._client = client
        self._db_url = db_url
        self._interval = interval

    async def run(self) -> None:
        logger.info("starting refunder loop (interval=%ds)", self._interval)
        while True:
            await self._process_expired_orders()
            await asyncio.sleep(self._interval)

    async def _process_expired_orders(self) -> None:
        logger.debug("checking for expired ethflow orders")
        # Query ethflow_orders table for expired orders needing refund
