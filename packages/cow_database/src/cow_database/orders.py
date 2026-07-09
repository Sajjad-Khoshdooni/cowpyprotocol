"""Order database queries — port of database/orders.rs."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

import asyncpg
from cow_bytes_hex import decode_hex

INSERT_ORDER_QUERY = """
INSERT INTO orders (
    uid, owner, creation_timestamp, sell_token, buy_token, receiver,
    sell_amount, buy_amount, valid_to, app_data, fee_amount, kind,
    partially_fillable, signature, signing_scheme, settlement_contract,
    sell_token_balance, buy_token_balance, cancellation_timestamp, class, true_valid_to
) VALUES (
    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21
) ON CONFLICT (uid) DO NOTHING
RETURNING uid
"""


async def insert_order(conn: asyncpg.Connection, order: dict[str, Any]) -> bool:
    """Insert an order, returning True if inserted."""
    uid = decode_hex(order["uid"]) if order["uid"].startswith("0x") else bytes.fromhex(order["uid"])
    result = await conn.fetchrow(
        INSERT_ORDER_QUERY,
        uid,
        decode_hex(order["owner"][2:]),
        order.get("creation_timestamp", datetime.utcnow()),
        decode_hex(order["sell_token"][2:]),
        decode_hex(order["buy_token"][2:]),
        decode_hex(order["receiver"][2:]) if order.get("receiver") else None,
        Decimal(str(order["sell_amount"])),
        Decimal(str(order["buy_amount"])),
        order["valid_to"],
        decode_hex(order["app_data"][2:])
        if order["app_data"].startswith("0x")
        else order["app_data"],
        Decimal(str(order["fee_amount"])),
        order["kind"],
        order.get("partially_fillable", False),
        decode_hex(order["signature"][2:]) if order.get("signature", "0x") != "0x" else b"",
        order.get("signing_scheme", "eip712"),
        decode_hex(order["settlement_contract"][2:]),
        order.get("sell_token_balance", "erc20"),
        order.get("buy_token_balance", "erc20"),
        order.get("cancellation_timestamp"),
        order.get("class", "market"),
        order["valid_to"],
    )
    return result is not None


async def get_order_by_uid(conn: asyncpg.Connection, uid: str) -> asyncpg.Record | None:
    uid_bytes = decode_hex(uid[2:] if uid.startswith("0x") else uid)
    return await conn.fetchrow("SELECT * FROM orders WHERE uid = $1", uid_bytes)


async def get_orders_by_owner(
    conn: asyncpg.Connection, owner: str, offset: int = 0, limit: int = 10
) -> list[asyncpg.Record]:
    owner_bytes = decode_hex(owner[2:])
    return await conn.fetch(
        "SELECT * FROM orders WHERE owner = $1 ORDER BY creation_timestamp DESC OFFSET $2 LIMIT $3",
        owner_bytes,
        offset,
        limit,
    )
