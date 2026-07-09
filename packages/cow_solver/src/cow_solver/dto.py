"""Solver DTOs — port of solvers-dto."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AuctionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    orders: list[dict[str, Any]]
    liquidity: list[dict[str, Any]] = []
    deadline: int | None = None


class Solution(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    solver: str
    score: float
    clearing_prices: dict[str, str] = Field(default_factory=dict, alias="clearingPrices")
    trades: list[dict[str, Any]] = []
    interactions: list[dict[str, Any]] = []
