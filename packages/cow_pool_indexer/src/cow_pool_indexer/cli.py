"""Pool indexer CLI."""

from __future__ import annotations

from pathlib import Path

import typer
import uvicorn
from cow_observe import configure_logging

from cow_pool_indexer.app import create_app

app = typer.Typer()


@app.command()
def main(
    config: Path = typer.Option(..., "--config"),
    addr: str = typer.Option("0.0.0.0:8081", "--addr"),
) -> None:
    configure_logging()
    host, port = addr.rsplit(":", 1)
    uvicorn.run(create_app(), host=host, port=int(port))


if __name__ == "__main__":
    app()
