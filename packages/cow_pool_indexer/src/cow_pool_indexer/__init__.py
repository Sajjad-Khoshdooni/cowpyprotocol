"""Pool indexer service — port of crates/pool-indexer."""

from cow_pool_indexer.app import create_app

__all__ = ["create_app"]
