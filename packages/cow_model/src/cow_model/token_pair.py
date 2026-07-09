"""Token pair and domain separator types."""

from __future__ import annotations

from typing import Annotated, Any

from eth_utils import to_checksum_address
from pydantic import BeforeValidator, PlainSerializer


def _validate_address(value: Any) -> str:
    if isinstance(value, str):
        if not value.startswith("0x"):
            raise ValueError("address must be 0x-prefixed")
        return to_checksum_address(value)
    raise TypeError(f"expected str address, got {type(value)}")


Address = Annotated[
    str, BeforeValidator(_validate_address), PlainSerializer(lambda v: v, return_type=str)
]


class TokenPair:
    """ERC20 token pair with sorted addresses."""

    def __init__(self, token_a: str, token_b: str) -> None:
        a, b = to_checksum_address(token_a), to_checksum_address(token_b)
        if a == b:
            raise ValueError("token pair addresses must differ")
        self._tokens = (min(a, b), max(a, b))

    @classmethod
    def new(cls, token_a: str, token_b: str) -> TokenPair | None:
        try:
            return cls(token_a, token_b)
        except ValueError:
            return None

    def contains(self, token: str) -> bool:
        t = to_checksum_address(token)
        return t in self._tokens

    def other(self, token: str) -> str | None:
        t = to_checksum_address(token)
        if t == self._tokens[0]:
            return self._tokens[1]
        if t == self._tokens[1]:
            return self._tokens[0]
        return None

    def get(self) -> tuple[str, str]:
        return self._tokens

    def __iter__(self):
        return iter(self._tokens)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TokenPair):
            return NotImplemented
        return self._tokens == other._tokens

    def __hash__(self) -> int:
        return hash(self._tokens)


class DomainSeparator:
    """EIP-712 domain separator (32 bytes)."""

    def __init__(self, value: bytes | str) -> None:
        if isinstance(value, str):
            from cow_bytes_hex import decode_hex

            value = decode_hex(value)
        if len(value) != 32:
            raise ValueError("domain separator must be 32 bytes")
        self.value = value

    @classmethod
    def from_chain(cls, chain_id: int, contract_address: str) -> DomainSeparator:
        from eth_account.messages import hash_domain

        domain_hash = hash_domain(
            {
                "name": "Gnosis Protocol",
                "version": "v2",
                "chainId": chain_id,
                "verifyingContract": to_checksum_address(contract_address),
            }
        )
        return cls(domain_hash)

    def __repr__(self) -> str:
        return self.value.hex()
