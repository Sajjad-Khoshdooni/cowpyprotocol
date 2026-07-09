"""Solana indexer CLI."""

from __future__ import annotations

import asyncio

import typer
from cow_observe import configure_logging

from cow_solana_indexer.indexer import SolanaIndexer

app = typer.Typer()


@app.command()
def main(
    grpc_url: str = typer.Option("http://localhost:10000", "--grpc-url"),
    db_url: str = typer.Option("postgresql://localhost/cow", "--db-url"),
) -> None:
    configure_logging()
    indexer = SolanaIndexer(grpc_url=grpc_url, db_url=db_url)
    asyncio.run(indexer.run())


if __name__ == "__main__":
    app()
