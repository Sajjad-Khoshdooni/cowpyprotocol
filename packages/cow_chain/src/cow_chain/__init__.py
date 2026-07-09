"""Chain metadata — port of crates/chain."""

from __future__ import annotations

from enum import Enum


class Chain(str, Enum):
    MAINNET = "mainnet"
    GNOSIS = "gnosis"
    ARBITRUM = "arbitrum"
    BASE = "base"
    SEPOLIA = "sepolia"
    POLYGON = "polygon"
    AVALANCHE = "avalanche"
    BNB = "bnb"
    LINEA = "linea"
    PLASMA = "plasma"


CHAIN_IDS: dict[Chain, int] = {
    Chain.MAINNET: 1,
    Chain.GNOSIS: 100,
    Chain.ARBITRUM: 42161,
    Chain.BASE: 8453,
    Chain.SEPOLIA: 11155111,
    Chain.POLYGON: 137,
    Chain.AVALANCHE: 43114,
    Chain.BNB: 56,
    Chain.LINEA: 59144,
    Chain.PLASMA: 9745,
}


SETTLEMENT_ADDRESSES: dict[Chain, str] = {
    Chain.MAINNET: "0x9008D19f58AAbD9eD0D60971565AA8510560ab41",
    Chain.GNOSIS: "0x9008D19f58AAbD9eD0D60971565AA8510560ab41",
    Chain.ARBITRUM: "0x9008D19f58AAbD9eD0D60971565AA8510560ab41",
    Chain.BASE: "0x9008D19f58AAbD9eD0D60971565AA8510560ab41",
    Chain.SEPOLIA: "0x9008D19f58AAbD9eD0D60971565AA8510560ab41",
}


def chain_from_id(chain_id: int) -> Chain | None:
    for chain, cid in CHAIN_IDS.items():
        if cid == chain_id:
            return chain
    return None
