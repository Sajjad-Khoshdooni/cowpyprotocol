"""Signature validation — port of signature-validator with real EIP-712 recovery."""

from __future__ import annotations

from cow_model import OrderCreation, SigningScheme
from cow_model.eip712 import hashed_eip712_message, hashed_ethsign_message
from cow_model.order_uid import hash_order_struct
from eth_keys import keys
from eth_utils import to_checksum_address


def _normalize_v(v: int) -> int:
    if v in (0, 1):
        return v
    if v == 27:
        return 0
    if v == 28:
        return 1
    raise ValueError(f"invalid signature v value: {v}")


def _parse_signature(sig: str) -> bytes:
    raw = bytes.fromhex(sig[2:] if sig.startswith("0x") else sig)
    if len(raw) != 65:
        raise ValueError("ECDSA signature must be 65 bytes")
    v = _normalize_v(raw[64])
    return raw[:64] + bytes([v])


class SignatureValidator:
    """Validates EIP-712 and eth_sign signatures for CoW orders."""

    def __init__(self, domain_separator: bytes) -> None:
        if len(domain_separator) != 32:
            raise ValueError("domain separator must be 32 bytes")
        self._domain_separator = domain_separator

    def struct_hash(self, order: OrderCreation) -> bytes:
        return hash_order_struct(order)

    def signing_hash(self, order: OrderCreation, scheme: SigningScheme) -> bytes:
        struct_hash = self.struct_hash(order)
        if scheme == SigningScheme.EIP712:
            return hashed_eip712_message(self._domain_separator, struct_hash)
        if scheme == SigningScheme.ETH_SIGN:
            return hashed_ethsign_message(self._domain_separator, struct_hash)
        raise ValueError(f"scheme {scheme} does not support off-chain ECDSA recovery")

    def recover_signer(self, order: OrderCreation) -> str:
        scheme = SigningScheme(order.signing_scheme.lower())
        if scheme in (SigningScheme.EIP1271, SigningScheme.PRE_SIGN):
            raise NotImplementedError(f"{scheme.value} requires on-chain validation")

        message_hash = self.signing_hash(order, scheme)
        sig_bytes = _parse_signature(order.signature)
        signature = keys.Signature(signature_bytes=sig_bytes)
        public_key = signature.recover_public_key_from_msg_hash(message_hash)
        return public_key.to_checksum_address()

    def validate_owner(self, order: OrderCreation, expected_owner: str | None = None) -> str:
        recovered = to_checksum_address(self.recover_signer(order))
        if expected_owner and recovered != to_checksum_address(expected_owner):
            raise ValueError(f"signer {recovered} does not match expected {expected_owner}")
        if order.from_ and recovered != to_checksum_address(order.from_):
            raise ValueError(f"signer {recovered} does not match from {order.from_}")
        return recovered
