"""PostgreSQL integration tests for order persistence."""

from __future__ import annotations

import os
from datetime import UTC, datetime

import pytest
from cow_configs import DatabasePoolConfig
from cow_database import create_pool
from cow_database.orders import get_order_by_uid, insert_order
from cow_model import OrderCreation, OrderKind, compute_order_uid

DOMAIN = bytes.fromhex("74e0b11bd18120612556bae4578cfd3a254d7e2495f543c569a92ff5794d9b09")
OWNER = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"


def _sample_order() -> OrderCreation:
    return OrderCreation(
        sellToken="0x0101010101010101010101010101010101010101",
        buyToken="0x0202020202020202020202020202020202020202",
        receiver="0x0303030303030303030303030303030303030303",
        sellAmount=1000,
        buyAmount=900,
        validTo=int(datetime.now(UTC).timestamp()) + 3600,
        appData="0x0000000000000000000000000000000000000000000000000000000000000000",
        feeAmount=10,
        kind=OrderKind.SELL,
        partiallyFillable=False,
        signingScheme="eip712",
        signature="0x" + "00" * 65,
        from_=OWNER,
    )


@pytest.fixture
async def db_pool():
    write_url = os.environ.get("DB_WRITE_URL")
    if not write_url:
        pytest.skip("DB_WRITE_URL not set")
    pool = await create_pool(DatabasePoolConfig(write_url=write_url, read_url=write_url))
    yield pool
    await pool.close()


@pytest.mark.postgres
@pytest.mark.asyncio
async def test_insert_and_fetch_order_with_computed_uid(db_pool) -> None:
    order = _sample_order()
    uid = compute_order_uid(order, DOMAIN, OWNER)

    async with db_pool.transaction() as conn:
        inserted = await insert_order(
            conn,
            {
                "uid": uid,
                "owner": OWNER,
                "sell_token": order.sell_token,
                "buy_token": order.buy_token,
                "receiver": order.receiver,
                "sell_amount": order.sell_amount,
                "buy_amount": order.buy_amount,
                "valid_to": order.valid_to,
                "app_data": order.app_data,
                "fee_amount": order.fee_amount,
                "kind": order.kind.value,
                "partially_fillable": order.partially_fillable,
                "signature": order.signature,
                "signing_scheme": order.signing_scheme,
                "settlement_contract": "0x9008D19f58AAbD9eD0D60971565AA8510560ab41",
                "sell_token_balance": order.sell_token_balance.value,
                "buy_token_balance": order.buy_token_balance.value,
                "class": "market",
            },
        )
        assert inserted is True

        row = await get_order_by_uid(conn, uid)
        assert row is not None
        assert row["owner"].hex() == OWNER[2:].lower()
        assert row["uid"].hex() == uid[2:]
