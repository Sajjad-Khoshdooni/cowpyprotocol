"""Interaction types — port of model/interaction.rs."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from cow_model.token_pair import Address


class InteractionData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    target: Address
    value: str = "0"
    call_data: str = Field(default="0x", alias="callData")


class Interactions(BaseModel):
    pre: list[InteractionData] = []
    post: list[InteractionData] = []
