"""Trade types — port of model/trade.rs."""

from __future__ import annotations

from datetime import datetime

from cow_number import U256
from pydantic import BaseModel, ConfigDict, Field

from cow_model.order import OrderUid
from cow_model.token_pair import Address


class Trade(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    block_number: int = Field(alias="blockNumber")
    log_index: int = Field(alias="logIndex")
    order_uid: OrderUid = Field(alias="orderUid")
    owner: Address
    sell_token: Address = Field(alias="sellToken")
    buy_token: Address = Field(alias="buyToken")
    sell_amount: U256 = Field(alias="sellAmount")
    buy_amount: U256 = Field(alias="buyAmount")
    fee_amount: U256 = Field(alias="feeAmount")
    execution: str | None = None
    tx_hash: str | None = Field(default=None, alias="txHash")
    timestamp: datetime | None = None
