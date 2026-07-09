"""Hex byte array helpers matching the Rust `bytes-hex` crate."""

from __future__ import annotations


def encode_prefixed(data: bytes) -> str:
    return "0x" + data.hex()


def decode_hex(value: str) -> bytes:
    if value.startswith("0x") or value.startswith("0X"):
        value = value[2:]
    return bytes.fromhex(value)


def encode_to_slice(data: bytes) -> str:
    return data.hex()
