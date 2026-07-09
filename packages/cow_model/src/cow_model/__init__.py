"""CoW Protocol domain models — port of crates/model."""

from cow_model.fee_policy import FeePolicy
from cow_model.interaction import InteractionData, Interactions
from cow_model.order import (
    BUY_ETH_ADDRESS,
    BuyTokenDestination,
    Order,
    OrderClass,
    OrderCreation,
    OrderData,
    OrderKind,
    OrderMetadata,
    OrderStatus,
    OrderUid,
    SellTokenSource,
)
from cow_model.order_uid import ComputedOrderUid, compute_order_uid
from cow_model.quote import PriceQuality, Quote, QuoteId, QuoteRequest, QuoteSigningScheme
from cow_model.signature import EcdsaSignature, Signature, SigningScheme
from cow_model.time import Timestamp
from cow_model.token_pair import DomainSeparator, TokenPair
from cow_model.trade import Trade

AuctionId = int

__all__ = [
    "AuctionId",
    "BUY_ETH_ADDRESS",
    "BuyTokenDestination",
    "ComputedOrderUid",
    "compute_order_uid",
    "DomainSeparator",
    "EcdsaSignature",
    "FeePolicy",
    "InteractionData",
    "Interactions",
    "Order",
    "OrderClass",
    "OrderCreation",
    "OrderData",
    "OrderKind",
    "OrderMetadata",
    "OrderStatus",
    "OrderUid",
    "PriceQuality",
    "Quote",
    "QuoteId",
    "QuoteRequest",
    "QuoteSigningScheme",
    "SellTokenSource",
    "Signature",
    "SigningScheme",
    "Timestamp",
    "TokenPair",
    "Trade",
]
