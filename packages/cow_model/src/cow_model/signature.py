"""Signature types — port of model/signature.rs."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SigningScheme(str, Enum):
    EIP712 = "eip712"
    ETH_SIGN = "ethsign"
    EIP1271 = "eip1271"
    PRE_SIGN = "presign"


class EcdsaSignature(BaseModel):
    r: str
    s: str
    v: int


class Signature(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    signing_scheme: SigningScheme = Field(default=SigningScheme.EIP712, alias="signingScheme")
    signature: str = "0x"

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Signature:
        scheme = data.get("signingScheme", "eip712")
        sig = data.get("signature", "0x")
        return cls(signingScheme=scheme, signature=sig)

    def to_bytes(self) -> bytes:
        from cow_bytes_hex import decode_hex

        if self.signing_scheme == SigningScheme.PRE_SIGN:
            return b""
        return decode_hex(self.signature)

    def scheme(self) -> SigningScheme:
        return self.signing_scheme
