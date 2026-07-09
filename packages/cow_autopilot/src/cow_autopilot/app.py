"""Autopilot internal HTTP API."""

from __future__ import annotations

from cow_observe.metrics import metrics_endpoint
from fastapi import FastAPI, Response

from cow_autopilot.run_loop import AuctionRunLoop


def create_app(run_loop: AuctionRunLoop) -> FastAPI:
    app = FastAPI(title="CoW Protocol Autopilot", version="0.1.0")
    app.state.run_loop = run_loop

    @app.get("/native_price/{token}")
    async def native_price(token: str) -> dict[str, str]:
        return {"token": token, "price": "0"}

    @app.get("/metrics")
    async def metrics() -> Response:
        content, content_type = metrics_endpoint()
        return Response(content=content, media_type=content_type)

    return app
