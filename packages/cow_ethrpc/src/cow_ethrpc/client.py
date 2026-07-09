"""Extended Ethereum RPC client."""

from __future__ import annotations

from typing import Any

from web3 import AsyncWeb3
from web3.providers import AsyncHTTPProvider


class EthRpcClient:
    """Async Web3 RPC client with batching support."""

    def __init__(self, node_url: str, *, max_batch_size: int = 100) -> None:
        self._w3 = AsyncWeb3(AsyncHTTPProvider(node_url))
        self._max_batch_size = max_batch_size

    @property
    def web3(self) -> AsyncWeb3:
        return self._w3

    async def chain_id(self) -> int:
        return await self._w3.eth.chain_id

    async def block_number(self) -> int:
        return await self._w3.eth.block_number

    async def get_block(self, number: int | str = "latest") -> dict[str, Any]:
        return await self._w3.eth.get_block(number)

    async def call(self, transaction: dict[str, Any], block: str = "latest") -> bytes:
        return await self._w3.eth.call(transaction, block)

    async def estimate_gas(self, transaction: dict[str, Any]) -> int:
        return await self._w3.eth.estimate_gas(transaction)

    async def gas_price(self) -> int:
        return await self._w3.eth.gas_price

    async def get_balance(self, address: str, block: str = "latest") -> int:
        return await self._w3.eth.get_balance(address, block)

    async def get_code(self, address: str, block: str = "latest") -> bytes:
        return await self._w3.eth.get_code(address, block)
