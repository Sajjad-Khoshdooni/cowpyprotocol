"""Refunder CLI."""

from __future__ import annotations

import asyncio

import typer
from cow_ethrpc import EthRpcClient
from cow_observe import configure_logging

from cow_refunder.runner import RefunderRunner

app = typer.Typer()


@app.command()
def main(
    node_url: str = typer.Option("http://localhost:8545", "--ethrpc"),
    db_url: str = typer.Option("postgresql://localhost/cow", "--db-url"),
    interval: int = typer.Option(60, "--interval"),
) -> None:
    configure_logging()
    client = EthRpcClient(node_url)
    runner = RefunderRunner(client=client, db_url=db_url, interval=interval)
    asyncio.run(runner.run())


if __name__ == "__main__":
    app()
