"""Signature recovery tests — vectors from GPv2Signing.test.ts / model/order.rs."""

from cow_model import OrderCreation, OrderKind, SigningScheme
from cow_model.order import BuyTokenDestination, SellTokenSource
from cow_shared import SignatureValidator


def _gpv2_test_order(signing_scheme: str, signature: str) -> OrderCreation:
    return OrderCreation(
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
        signingScheme=signing_scheme,
        signature=signature,
    )


DOMAIN = bytes.fromhex("74e0b11bd18120612556bae4578cfd3a254d7e2495f543c569a92ff5794d9b09")
EXPECTED_OWNER = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"


def test_recover_eip712_signature_from_contract_test_vector() -> None:
    order = _gpv2_test_order(
        "eip712",
        "0x59c0f5c151071c1320575f6da826a6c276525bbe733234bad1afb2879657d65d"
        "2afe6812746f4cc97f28f3a5dfdbfc7087511695d23da5e9792cd7ed6c9ddeb7"
        "1c",
    )
    validator = SignatureValidator(DOMAIN)
    assert validator.recover_signer(order) == EXPECTED_OWNER


def test_recover_ethsign_signature_from_contract_test_vector() -> None:
    order = _gpv2_test_order(
        "ethsign",
        "0xbf3bc5a9b60d08dc05768320553ba59a6f301d985903618cfc002e8a61cb78b5"
        "5d4a474a43a60193d90cda35ff2764f3913b47e5b5b87770064f549fe871afcc"
        "1b",
    )
    validator = SignatureValidator(DOMAIN)
    assert validator.recover_signer(order) == EXPECTED_OWNER


def test_validate_owner_matches_from_field() -> None:
    order = _gpv2_test_order(
        SigningScheme.EIP712.value,
        "0x59c0f5c151071c1320575f6da826a6c276525bbe733234bad1afb2879657d65d"
        "2afe6812746f4cc97f28f3a5dfdbfc7087511695d23da5e9792cd7ed6c9ddeb7"
        "1c",
    )
    order.from_ = EXPECTED_OWNER
    validator = SignatureValidator(DOMAIN)
    assert validator.validate_owner(order) == EXPECTED_OWNER
