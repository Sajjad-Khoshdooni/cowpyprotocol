"""Settlement simulation — port of simulator crate."""

from __future__ import annotations

from typing import Any

from cow_ethrpc import EthRpcClient


class SettlementSimulator:
    """Simulates settlement transactions via eth_call."""

    def __init__(self, client: EthRpcClient) -> None:
        self._client = client

    async def simulate(self, transaction: dict[str, Any]) -> bytes:
        return await self._client.call(transaction)

    async def estimate_gas(self, transaction: dict[str, Any]) -> int:
        return await self._client.estimate_gas(transaction)


__all__ = ["SettlementSimulator"]
