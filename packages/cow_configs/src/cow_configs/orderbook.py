"""Orderbook configuration — port of configs/orderbook/mod.rs."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from cow_configs.database import DatabasePoolConfig
from cow_configs.shared import SharedConfig


class VolumeFeeConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    factor: float | None = None
    effective_from_timestamp: datetime | None = Field(
        default=None, alias="effective-from-timestamp"
    )


class NativePriceEstimatorConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    type: str
    name: str | None = None
    url: str | None = None


class NativePriceEstimationConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    estimators: list[list[NativePriceEstimatorConfig]] = []


class PriceEstimationDriverConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    name: str
    url: str


class OrderQuotingConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    price_estimation_drivers: list[PriceEstimationDriverConfig] = Field(
        default_factory=list, alias="price-estimation-drivers"
    )


class OrderValidationConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    max_order_validity_period: str | None = Field(default=None, alias="max-order-validity-period")


class BannedUsersConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    addresses: list[str] = []


class OrderbookConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    shared: SharedConfig = Field(default_factory=SharedConfig)
    bind_address: str = Field(default="0.0.0.0:8080", alias="bind-address")
    order_validation: OrderValidationConfig = Field(
        default_factory=OrderValidationConfig, alias="order-validation"
    )
    banned_users: BannedUsersConfig = Field(default_factory=BannedUsersConfig, alias="banned-users")
    volume_fee: VolumeFeeConfig | None = Field(default=None, alias="volume-fee")
    app_data_size_limit: int = Field(default=8192, alias="app-data-size-limit")
    active_order_competition_threshold: int = Field(
        default=5, alias="active-order-competition-threshold"
    )
    unsupported_tokens: list[str] = Field(default_factory=list, alias="unsupported-tokens")
    eip1271_skip_creation_validation: bool = Field(
        default=False, alias="eip1271-skip-creation-validation"
    )
    database: DatabasePoolConfig = Field(default_factory=DatabasePoolConfig)
    native_price_estimation: NativePriceEstimationConfig | None = Field(
        default=None, alias="native-price-estimation"
    )
    order_quoting: OrderQuotingConfig | None = Field(default=None, alias="order-quoting")
