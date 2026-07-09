"""Quote types — port of model/quote.rs."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from cow_number import U256
from pydantic import BaseModel, ConfigDict, Field

from cow_model.order import BuyTokenDestination, OrderKind, SellTokenSource
from cow_model.token_pair import Address


class PriceQuality(str, Enum):
    FAST = "fast"
    OPTIMAL = "optimal"
    VERIFIED = "verified"


class QuoteSigningScheme(str, Enum):
    EIP712 = "eip712"
    ETH_SIGN = "ethsign"
    EIP1271 = "eip1271"
    PRE_SIGN = "presign"


QuoteId = int


class QuoteRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    sell_token: Address = Field(alias="sellToken")
    buy_token: Address = Field(alias="buyToken")
    kind: OrderKind
    sell_amount_before_fee: U256 | None = Field(default=None, alias="sellAmountBeforeFee")
    sell_amount_after_fee: U256 | None = Field(default=None, alias="sellAmountAfterFee")
    buy_amount_after_fee: U256 | None = Field(default=None, alias="buyAmountAfterFee")
    from_: Address | None = Field(default=None, alias="from")
    price_quality: PriceQuality = Field(default=PriceQuality.OPTIMAL, alias="priceQuality")
    signing_scheme: QuoteSigningScheme = Field(
        default=QuoteSigningScheme.EIP712, alias="signingScheme"
    )
    onchain_order: bool = Field(default=False, alias="onchainOrder")
    verification_gas_limit: int | None = Field(default=None, alias="verificationGasLimit")


class Quote(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: QuoteId | None = None
    sell_token: Address = Field(alias="sellToken")
    buy_token: Address = Field(alias="buyToken")
    sell_amount: U256 = Field(alias="sellAmount")
    buy_amount: U256 = Field(alias="buyAmount")
    fee_amount: U256 = Field(alias="feeAmount")
    expiration: datetime | None = None
    kind: OrderKind
    partially_fillable: bool = Field(default=False, alias="partiallyFillable")
    sell_token_balance: SellTokenSource = Field(
        default=SellTokenSource.ERC20, alias="sellTokenBalance"
    )
    buy_token_balance: BuyTokenDestination = Field(
        default=BuyTokenDestination.ERC20, alias="buyTokenBalance"
    )
    verified: bool = False
