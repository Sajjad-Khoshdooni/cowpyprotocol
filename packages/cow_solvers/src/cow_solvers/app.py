"""Solver engine HTTP API."""

from __future__ import annotations

from typing import Any

from cow_observe.metrics import metrics_endpoint
from cow_solver import AuctionRequest, Solution
from fastapi import FastAPI, Response


def create_app(engine: str = "baseline") -> FastAPI:
    app = FastAPI(title=f"CoW Solver ({engine})", version="0.1.0")

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok", "engine": engine}

    @app.get("/metrics")
    async def metrics() -> Response:
        content, content_type = metrics_endpoint()
        return Response(content=content, media_type=content_type)

    @app.post("/solve")
    async def solve(auction: AuctionRequest) -> dict[str, Any]:
        solution = Solution(
            solver=engine,
            score=float(len(auction.orders)),
            trades=[{"orderUid": o.get("uid", "")} for o in auction.orders],
        )
        return {"solutions": [solution.model_dump(by_alias=True)]}

    return app
