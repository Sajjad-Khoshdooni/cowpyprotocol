"""Autopilot CLI."""

from __future__ import annotations

import asyncio
from pathlib import Path

import typer
import uvicorn
from cow_ethrpc import EthRpcClient
from cow_observe import configure_logging

from cow_autopilot.app import create_app
from cow_autopilot.run_loop import AuctionRunLoop

app = typer.Typer()


@app.command()
def main(
    config: Path = typer.Option(..., "--config"),
    addr: str = typer.Option("0.0.0.0:12088", "--addr"),
    run_loop: bool = typer.Option(True, "--run-loop/--no-run-loop"),
) -> None:
    configure_logging()
    host, port = addr.rsplit(":", 1)
    client = EthRpcClient("http://localhost:8545")
    loop = AuctionRunLoop(client=client, db=None)
    if run_loop:
        asyncio.get_event_loop().create_task(loop.run())
    uvicorn.run(create_app(loop), host=host, port=int(port))


if __name__ == "__main__":
    app()
