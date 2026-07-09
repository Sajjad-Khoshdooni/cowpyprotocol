"""Unit tests for cow_model."""

from cow_model import Order, OrderKind, OrderStatus, QuoteRequest


def test_order_kind_values() -> None:
    assert OrderKind.SELL.value == "sell"
    assert OrderKind.BUY.value == "buy"


def test_order_status_defaults() -> None:
    order = Order(
        sellToken="0x0000000000000000000000000000000000000001",
        buyToken="0x0000000000000000000000000000000000000002",
        sellAmount="1000",
        buyAmount="900",
        validTo=9999999999,
        appData="0x" + "0" * 64,
        feeAmount="10",
        kind=OrderKind.SELL,
        partiallyFillable=False,
    )
    assert order.status == OrderStatus.OPEN


def test_quote_request_camel_case() -> None:
    req = QuoteRequest.model_validate(
        {
            "sellToken": "0x0000000000000000000000000000000000000001",
            "buyToken": "0x0000000000000000000000000000000000000002",
            "kind": "sell",
            "sellAmountBeforeFee": "1000",
        }
    )
    assert req.sell_token.endswith("1")
