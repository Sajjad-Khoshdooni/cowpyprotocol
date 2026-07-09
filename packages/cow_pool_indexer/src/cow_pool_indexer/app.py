"""Pool indexer HTTP API."""

from __future__ import annotations

from typing import Any

from cow_observe.metrics import metrics_endpoint
from fastapi import FastAPI, Response


def create_app() -> FastAPI:
    app = FastAPI(title="CoW Pool Indexer", version="0.1.0")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/v1/{network}/uniswap/v3/pools")
    async def list_pools(network: str) -> list[dict[str, Any]]:
        return []

    @app.get("/api/v1/{network}/uniswap/v3/pools/by-ids")
    async def pools_by_ids(network: str, ids: str = "") -> list[dict[str, Any]]:
        return []

    @app.get("/api/v1/{network}/uniswap/v3/pools/ticks")
    async def pool_ticks(network: str) -> list[dict[str, Any]]:
        return []

    @app.get("/api/v1/{network}/uniswap/v3/pools/{pool_address}/ticks")
    async def pool_ticks_by_address(network: str, pool_address: str) -> list[dict[str, Any]]:
        return []

    @app.get("/metrics")
    async def metrics() -> Response:
        content, content_type = metrics_endpoint()
        return Response(content=content, media_type=content_type)

    return app
