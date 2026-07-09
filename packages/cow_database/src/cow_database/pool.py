"""PostgreSQL connection pool — port of database/lib.rs."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import asyncpg
from cow_configs import DatabasePoolConfig

TABLES = [
    "app_data",
    "auctions",
    "cow_amms",
    "ethflow_orders",
    "ethflow_refunds",
    "interactions",
    "invalidations",
    "jit_orders",
    "last_indexed_blocks",
    "onchain_order_invalidations",
    "onchain_placed_orders",
    "presignature_events",
    "proposed_jit_orders",
    "quotes",
    "reference_scores",
    "settlement_executions",
    "settlements",
    "solver_competitions",
    "surplus_capturing_jit_order_owners",
    "trades",
]


class Postgres:
    """Async PostgreSQL connection pool wrapper."""

    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    @classmethod
    async def create(cls, config: DatabasePoolConfig) -> Postgres:
        pool = await asyncpg.create_pool(
            dsn=config.write_url,
            min_size=1,
            max_size=config.max_connections,
            command_timeout=config.statement_timeout_seconds,
        )
        return cls(pool)

    @classmethod
    async def create_read(cls, config: DatabasePoolConfig) -> Postgres:
        pool = await asyncpg.create_pool(
            dsn=config.effective_read_url(),
            min_size=1,
            max_size=config.max_connections,
            command_timeout=config.statement_timeout_seconds,
        )
        return cls(pool)

    async def close(self) -> None:
        await self._pool.close()

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[asyncpg.Connection]:
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                yield conn

    async def execute(self, query: str, *args) -> str:
        return await self._pool.execute(query, *args)

    async def fetch(self, query: str, *args) -> list[asyncpg.Record]:
        return await self._pool.fetch(query, *args)

    async def fetchrow(self, query: str, *args) -> asyncpg.Record | None:
        return await self._pool.fetchrow(query, *args)

    async def fetchval(self, query: str, *args):
        return await self._pool.fetchval(query, *args)


async def create_pool(config: DatabasePoolConfig) -> Postgres:
    return await Postgres.create(config)
