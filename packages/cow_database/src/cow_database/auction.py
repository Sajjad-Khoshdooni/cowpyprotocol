"""Auction database queries — port of database/auction.rs."""

from __future__ import annotations

import asyncpg


async def get_current_auction(conn: asyncpg.Connection) -> asyncpg.Record | None:
    return await conn.fetchrow("SELECT id, json FROM auctions ORDER BY id DESC LIMIT 1")
