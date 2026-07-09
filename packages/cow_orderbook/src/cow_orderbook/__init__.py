"""Orderbook HTTP API service — port of crates/orderbook."""

from cow_orderbook.app import create_app

__all__ = ["create_app"]
