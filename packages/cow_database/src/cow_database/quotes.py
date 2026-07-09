"""Quote database queries — port of database/quotes.rs."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

import asyncpg


async def insert_quote(conn: asyncpg.Connection, quote: dict[str, Any]) -> int:
    return await conn.fetchval(
        """
        INSERT INTO quotes (
            sell_token, buy_token, sell_amount, buy_amount, fee_amount,
            kind, partially_fillable, expiration, verified
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING id
        """,
        quote["sell_token"],
        quote["buy_token"],
        Decimal(str(quote["sell_amount"])),
        Decimal(str(quote["buy_amount"])),
        Decimal(str(quote["fee_amount"])),
        quote["kind"],
        quote.get("partially_fillable", False),
        quote.get("expiration", datetime.utcnow()),
        quote.get("verified", False),
    )
