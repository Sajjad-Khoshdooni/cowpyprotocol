"""Liquidity source registry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from cow_ethrpc import EthRpcClient


@dataclass
class LiquiditySource:
    name: str
    kind: str  # uniswap_v2, uniswap_v3, balancer_v2, etc.


class LiquidityFetcher(Protocol):
    async def fetch(self) -> list[dict[str, Any]]: ...


class LiquidityRegistry:
    """Registry of configured liquidity sources."""

    def __init__(self, client: EthRpcClient) -> None:
        self._client = client
        self._sources: list[LiquiditySource] = []

    def register(self, source: LiquiditySource) -> None:
        self._sources.append(source)

    async def fetch_all(self) -> list[dict[str, Any]]:
        return [{"name": s.name, "kind": s.kind} for s in self._sources]
