"""Orderbook CLI entrypoint."""

from __future__ import annotations

import asyncio
from pathlib import Path

import typer
import uvicorn
from cow_configs import OrderbookConfig, load_toml_config
from cow_observe import configure_logging

from cow_orderbook.app import create_app
from cow_orderbook.state import build_state

app = typer.Typer()


async def _serve(cfg: OrderbookConfig, host: str, port: int) -> None:
    """Run uvicorn in the same event loop used to create the DB pool."""
    state = await build_state(cfg)
    fastapi_app = create_app(state)
    server = uvicorn.Server(
        uvicorn.Config(fastapi_app, host=host, port=port, log_level="info")
    )
    await server.serve()


@app.command()
def main(
    config: Path = typer.Option(..., "--config", help="Path to orderbook TOML config"),
    host: str | None = typer.Option(None, help="Override bind host"),
    port: int | None = typer.Option(None, help="Override bind port"),
) -> None:
    """Run the orderbook HTTP API service."""
    cfg = load_toml_config(config, OrderbookConfig)
    configure_logging(
        json_logs=cfg.shared.logging.use_json,
        filter_str=cfg.shared.logging.filter,
    )

    bind_host, bind_port = cfg.bind_address.rsplit(":", 1)
    asyncio.run(
        _serve(
            cfg,
            host=host or bind_host,
            port=port or int(bind_port),
        )
    )


if __name__ == "__main__":
    app()
