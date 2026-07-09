"""Shared configuration — port of configs/shared.rs."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from cow_configs.deserialize_env import resolve_env_url, resolve_optional_env_url


class GasEstimatorType(str, Enum):
    WEB3 = "Web3"
    ALLOY = "Alloy"


class LoggingConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    filter: str = Field(
        default="info,autopilot=debug,driver=debug,orderbook=debug",
        alias="filter",
    )
    use_json: bool = Field(default=False, alias="use-json")


class TracingConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    collector_endpoint: str | None = Field(default=None, alias="collector-endpoint")
    service_name: str | None = Field(default=None, alias="service-name")


class EthRpcConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    max_batch_size: int = Field(default=100, alias="max-batch-size")
    max_concurrent_requests: int = Field(default=10, alias="max-concurrent-requests")


class CurrentBlockConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    max_block_age: str | None = Field(default=None, alias="max-block-age")


class EventBusConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    url: str
    stream: str | None = None


class ContractAddresses(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    settlement: str | None = None
    vault_relayer: str | None = Field(default=None, alias="vault-relayer")


class SharedConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    ethrpc: EthRpcConfig = Field(default_factory=EthRpcConfig)
    current_block: CurrentBlockConfig = Field(
        default_factory=CurrentBlockConfig, alias="current-block"
    )
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    tracing: TracingConfig = Field(default_factory=TracingConfig)
    node_url: str = Field(default="http://localhost:8545", alias="node-url")
    simulation_node_url: str | None = Field(default=None, alias="simulation-node-url")
    chain_id: int | None = Field(default=None, alias="chain-id")
    gas_estimators: list[GasEstimatorType] = Field(
        default_factory=lambda: [GasEstimatorType.WEB3], alias="gas-estimators"
    )
    contracts: ContractAddresses = Field(default_factory=ContractAddresses)
    event_bus: EventBusConfig | None = Field(default=None, alias="event-bus")

    @field_validator("node_url", mode="before")
    @classmethod
    def resolve_node_url(cls, v: str) -> str:
        return resolve_env_url(v)

    @field_validator("simulation_node_url", mode="before")
    @classmethod
    def resolve_simulation_node_url(cls, v: str | None) -> str | None:
        return resolve_optional_env_url(v)

    @model_validator(mode="after")
    def validate_event_bus(self) -> SharedConfig:
        if self.event_bus is not None and self.chain_id is None:
            raise ValueError("chain-id is required when the event bus is configured")
        return self
