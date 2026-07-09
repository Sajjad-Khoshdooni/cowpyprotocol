"""Order types — port of model/order.rs."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Any

from cow_number import U256
from pydantic import BaseModel, ConfigDict, Field

from cow_model.token_pair import Address

BUY_ETH_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"

ORDER_UID_BYTES = 56


class OrderStatus(str, Enum):
    PRESIGNATURE_PENDING = "presignaturePending"
    OPEN = "open"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class OrderKind(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderClass(str, Enum):
    MARKET = "market"
    LIQUIDITY = "liquidity"
    LIMIT = "limit"


class SellTokenSource(str, Enum):
    ERC20 = "erc20"
    INTERNAL = "internal"
    EXTERNAL = "external"


class BuyTokenDestination(str, Enum):
    ERC20 = "erc20"
    INTERNAL = "internal"


def _validate_order_uid(value: Any) -> str:
    if isinstance(value, str):
        if value.startswith("0x"):
            value = value[2:]
        if len(value) != ORDER_UID_BYTES * 2:
            raise ValueError(f"order uid must be {ORDER_UID_BYTES} bytes")
        return "0x" + value.lower()
    raise TypeError("order uid must be a hex string")


OrderUid = Annotated[str, Field(pattern=r"^0x[0-9a-fA-F]{112}$")]


class OrderData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    sell_token: Address = Field(alias="sellToken")
    buy_token: Address = Field(alias="buyToken")
    receiver: Address | None = None
    sell_amount: U256 = Field(alias="sellAmount")
    buy_amount: U256 = Field(alias="buyAmount")
    valid_to: int = Field(alias="validTo")
    app_data: str = Field(alias="appData")
    fee_amount: U256 = Field(alias="feeAmount")
    kind: OrderKind
    partially_fillable: bool = Field(alias="partiallyFillable")
    sell_token_balance: SellTokenSource = Field(
        default=SellTokenSource.ERC20, alias="sellTokenBalance"
    )
    buy_token_balance: BuyTokenDestination = Field(
        default=BuyTokenDestination.ERC20, alias="buyTokenBalance"
    )


class OrderMetadata(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    creation_date: datetime | None = Field(default=None, alias="creationDate")
    owner: Address | None = None
    uid: OrderUid | None = None
    status: OrderStatus = OrderStatus.OPEN
    class_: OrderClass = Field(default=OrderClass.MARKET, alias="class")
    executed_sell_amount: U256 | None = Field(default=None, alias="executedSellAmount")
    executed_buy_amount: U256 | None = Field(default=None, alias="executedBuyAmount")
    invalidated: bool = False
    signing_scheme: str | None = Field(default=None, alias="signingScheme")
    signature: str | None = None


class Order(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    # Flattened metadata + data + signature
    creation_date: datetime | None = Field(default=None, alias="creationDate")
    owner: Address | None = None
    uid: OrderUid | None = None
    status: OrderStatus = OrderStatus.OPEN
    class_: OrderClass = Field(default=OrderClass.MARKET, alias="class")
    executed_sell_amount: U256 | None = Field(default=None, alias="executedSellAmount")
    executed_buy_amount: U256 | None = Field(default=None, alias="executedBuyAmount")
    invalidated: bool = False
    sell_token: Address = Field(alias="sellToken")
    buy_token: Address = Field(alias="buyToken")
    receiver: Address | None = None
    sell_amount: U256 = Field(alias="sellAmount")
    buy_amount: U256 = Field(alias="buyAmount")
    valid_to: int = Field(alias="validTo")
    app_data: str = Field(alias="appData")
    fee_amount: U256 = Field(alias="feeAmount")
    kind: OrderKind
    partially_fillable: bool = Field(alias="partiallyFillable")
    sell_token_balance: SellTokenSource = Field(
        default=SellTokenSource.ERC20, alias="sellTokenBalance"
    )
    buy_token_balance: BuyTokenDestination = Field(
        default=BuyTokenDestination.ERC20, alias="buyTokenBalance"
    )
    signing_scheme: str = Field(default="eip712", alias="signingScheme")
    signature: str = "0x"

    def is_user_order(self) -> bool:
        return self.class_ in (OrderClass.MARKET, OrderClass.LIMIT)

    def is_limit_order(self) -> bool:
        return self.class_ == OrderClass.LIMIT


class OrderCreation(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    sell_token: Address = Field(alias="sellToken")
    buy_token: Address = Field(alias="buyToken")
    receiver: Address | None = None
    sell_amount: U256 = Field(alias="sellAmount")
    buy_amount: U256 = Field(alias="buyAmount")
    valid_to: int = Field(alias="validTo")
    app_data: str = Field(alias="appData")
    fee_amount: U256 = Field(alias="feeAmount")
    kind: OrderKind
    partially_fillable: bool = Field(alias="partiallyFillable")
    sell_token_balance: SellTokenSource = Field(
        default=SellTokenSource.ERC20, alias="sellTokenBalance"
    )
    buy_token_balance: BuyTokenDestination = Field(
        default=BuyTokenDestination.ERC20, alias="buyTokenBalance"
    )
    signing_scheme: str = Field(default="eip712", alias="signingScheme")
    signature: str
    from_: Address | None = Field(default=None, alias="from")
    quote_id: int | None = Field(default=None, alias="quoteId")
