"""Driver HTTP API — port of driver API routes."""

from __future__ import annotations

from typing import Any

from cow_observe.metrics import metrics_endpoint
from cow_solver import AuctionRequest, Solution, select_winner
from fastapi import FastAPI, Response
from pydantic import BaseModel


class SettleRequest(BaseModel):
    solution_id: str | None = None


def create_app() -> FastAPI:
    app = FastAPI(title="CoW Protocol Driver", version="0.1.0")
    _solutions: list[Solution] = []

    @app.get("/")
    async def info() -> dict[str, str]:
        return {"service": "driver", "version": "0.1.0"}

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/metrics")
    async def metrics() -> Response:
        content, content_type = metrics_endpoint()
        return Response(content=content, media_type=content_type)

    @app.get("/gasprice")
    async def gasprice() -> dict[str, str]:
        return {"gasPrice": "0"}

    @app.get("/quote")
    async def quote(
        sellToken: str,
        buyToken: str,
        kind: str = "sell",
        sellAmount: str = "0",
        buyAmount: str = "0",
    ) -> dict[str, str]:
        return {
            "sellToken": sellToken,
            "buyToken": buyToken,
            "sellAmount": sellAmount,
            "buyAmount": buyAmount or sellAmount,
            "feeAmount": "0",
        }

    @app.post("/solve")
    async def solve(auction: AuctionRequest) -> dict[str, Any]:
        solution = Solution(solver="driver", score=1.0, trades=[])
        _solutions.append(solution)
        return {"solutions": [solution.model_dump(by_alias=True)]}

    @app.post("/settle")
    async def settle(request: SettleRequest) -> dict[str, str]:
        winner = select_winner(_solutions)
        return {"status": "submitted", "solver": winner.solver if winner else "none"}

    @app.post("/reveal")
    async def reveal() -> dict[str, Any]:
        return {"calldata": "0x", "interactions": []}

    return app
