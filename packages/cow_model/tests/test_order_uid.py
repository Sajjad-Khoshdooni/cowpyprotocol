"""Order UID tests — vectors from services/crates/model/src/order.rs."""

from cow_model import OrderCreation, OrderKind
from cow_model.order import BuyTokenDestination, SellTokenSource
from cow_model.order_uid import ComputedOrderUid, compute_order_uid, hash_order_struct
from eth_utils import to_checksum_address


def test_compute_order_uid_matches_rust_vector() -> None:
    """From model/order.rs::compute_order_uid (GPv2Signing.test.ts vector)."""
    domain = bytes.fromhex(
        "74e0b11bd18120612556bae4578cfd3a254d7e2495f543c569a92ff5794d9b09"
    )
    owner = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
    order = OrderCreation(
        sellToken="0x0101010101010101010101010101010101010101",
        buyToken="0x0202020202020202020202020202020202020202",
        receiver="0x0303030303030303030303030303030303030303",
        sellAmount=0x0246DDF97976680000,
        buyAmount=0x0B98BC829A6F90000,
        validTo=0xFFFFFFFF,
        appData="0x0000000000000000000000000000000000000000000000000000000000000000",
        feeAmount=0x0DE0B6B3A7640000,
        kind=OrderKind.SELL,
        partiallyFillable=False,
        sellTokenBalance=SellTokenSource.ERC20,
        buyTokenBalance=BuyTokenDestination.ERC20,
        signingScheme="eip712",
        signature="0x",
    )

    uid = ComputedOrderUid.compute(order, domain, owner)
    expected = (
        "0e45d31fd31b28c26031cdd81b35a8938b2ccca2cc425fcf440fd3bfed1eede9"
        "70997970c51812dc3a010c7d01b50e0d17dc79c8"
        "ffffffff"
    )
    assert uid.to_hex() == "0x" + expected
    assert compute_order_uid(order, domain, owner) == "0x" + expected


def test_order_uid_parts_roundtrip() -> None:
    digest = bytes([0xAB] * 32)
    owner = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
    uid = ComputedOrderUid.from_parts(digest, owner, 1234567890)
    got_digest, got_owner, got_valid_to = uid.parts()
    assert got_digest == digest
    assert got_owner == to_checksum_address(owner)
    assert got_valid_to == 1234567890


def test_hash_struct_is_deterministic() -> None:
    order = OrderCreation(
        sellToken="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        buyToken="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        sellAmount=1000,
        buyAmount=900,
        validTo=999999999,
        appData="0x0000000000000000000000000000000000000000000000000000000000000000",
        feeAmount=10,
        kind=OrderKind.SELL,
        partiallyFillable=False,
        signingScheme="eip712",
        signature="0x",
    )
    assert hash_order_struct(order) == hash_order_struct(order)
