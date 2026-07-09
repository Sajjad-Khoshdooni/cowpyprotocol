"""Gas price estimation — port of gas-price-estimation crate."""

from __future__ import annotations

from cow_ethrpc import EthRpcClient


class GasPriceEstimator:
    """Estimates gas price from Ethereum node."""

    def __init__(self, client: EthRpcClient) -> None:
        self._client = client

    async def estimate(self) -> int:
        return await self._client.gas_price()

    async def estimate_with_priority(self, priority_fee: int = 0) -> int:
        base = await self.estimate()
        return base + priority_fee
