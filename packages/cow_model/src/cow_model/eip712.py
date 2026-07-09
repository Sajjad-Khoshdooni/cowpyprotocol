"""EIP-712 helpers matching crates/model signature utilities."""

from __future__ import annotations

from eth_hash.auto import keccak

EIP712_MAGIC = b"\x19\x01"


def keccak256(data: bytes) -> bytes:
    return keccak(data)


def hashed_eip712_message(domain_separator: bytes, struct_hash: bytes) -> bytes:
    """Hash the EIP-712 signing payload: keccak256(0x1901 ‖ domain ‖ structHash)."""
    if len(domain_separator) != 32 or len(struct_hash) != 32:
        raise ValueError("domain separator and struct hash must be 32 bytes")
    return keccak256(EIP712_MAGIC + domain_separator + struct_hash)


def hashed_ethsign_message(domain_separator: bytes, struct_hash: bytes) -> bytes:
    """Hash for eth_sign scheme over an order struct."""
    inner = hashed_eip712_message(domain_separator, struct_hash)
    prefix = b"\x19Ethereum Signed Message:\n32"
    return keccak256(prefix + inner)
