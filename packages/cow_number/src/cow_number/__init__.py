"""U256 and numeric utilities matching the Rust `number` crate."""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Any

from pydantic import BeforeValidator, PlainSerializer

MAX_U256 = 2**256 - 1


def _validate_u256(value: Any) -> int:
    if isinstance(value, int):
        v = value
    elif isinstance(value, str):
        if value.startswith("0x") or value.startswith("0X"):
            v = int(value, 16)
        else:
            v = int(value)
    else:
        raise TypeError(f"expected int or str, got {type(value)}")
    if v < 0 or v > MAX_U256:
        raise ValueError(f"value {v} out of U256 range")
    return v


def _serialize_u256(value: int) -> str:
    return str(value)


U256 = Annotated[
    int, BeforeValidator(_validate_u256), PlainSerializer(_serialize_u256, return_type=str)
]


def u256_to_decimal(value: int) -> Decimal:
    return Decimal(value)


def decimal_to_u256(value: Decimal) -> int:
    i = int(value)
    if i < 0 or i > MAX_U256:
        raise ValueError(f"value {i} out of U256 range")
    return i
