"""Driver CLI."""

from __future__ import annotations

from pathlib import Path

import typer
import uvicorn
from cow_observe import configure_logging

from cow_driver.app import create_app

app = typer.Typer()


@app.command()
def main(
    config: Path = typer.Option(..., "--config"),
    addr: str = typer.Option("0.0.0.0:11088", "--addr"),
) -> None:
    configure_logging()
    host, port = addr.rsplit(":", 1)
    fastapi_app = create_app()
    uvicorn.run(fastapi_app, host=host, port=int(port))


if __name__ == "__main__":
    app()
