"""Solver competition types — port of model/solver_competition*.rs."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from cow_model.order import OrderUid


class SolverCompetition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    auction_id: int = Field(alias="auctionId")
    auction_start_block: int = Field(alias="auctionStartBlock")
    transaction_hash: str | None = Field(default=None, alias="transactionHash")
    orders: list[OrderUid] = []
    solutions: list[dict[str, Any]] = []


class SolverCompetitionV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    auction_id: int = Field(alias="auctionId")
    auction_start_block: int = Field(alias="auctionStartBlock")
    reference_scores: dict[str, Any] | None = Field(default=None, alias="referenceScores")
    solutions: list[dict[str, Any]] = []
