"""Solvers CLI with subcommands: baseline, okx, bitget."""

from __future__ import annotations

from pathlib import Path

import typer
import uvicorn
from cow_observe import configure_logging

from cow_solvers.app import create_app

app = typer.Typer()


def _run(engine: str, config: Path | None, addr: str) -> None:
    configure_logging()
    host, port = addr.rsplit(":", 1)
    fastapi_app = create_app(engine)
    uvicorn.run(fastapi_app, host=host, port=int(port))


@app.command()
def baseline(
    config: Path | None = typer.Option(None, "--config"),
    addr: str = typer.Option("0.0.0.0:11088", "--addr"),
) -> None:
    _run("baseline", config, addr)


@app.command()
def okx(
    config: Path | None = typer.Option(None, "--config"),
    addr: str = typer.Option("0.0.0.0:11089", "--addr"),
) -> None:
    _run("okx", config, addr)


@app.command()
def bitget(
    config: Path | None = typer.Option(None, "--config"),
    addr: str = typer.Option("0.0.0.0:11090", "--addr"),
) -> None:
    _run("bitget", config, addr)


if __name__ == "__main__":
    app()
