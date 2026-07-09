"""Fee policy types — port of model/fee_policy.rs."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class FeePolicyKind(str, Enum):
    SURPLUS = "surplus"
    PRICE_IMPROVEMENT = "priceImprovement"
    VOLUME = "volume"


class FeePolicy(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    kind: FeePolicyKind
    factor: float
    max_volume_factor: float | None = Field(default=None, alias="maxVolumeFactor")
