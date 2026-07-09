"""Application state."""

from __future__ import annotations

from dataclasses import dataclass

from cow_configs import OrderbookConfig
from cow_database import Postgres, create_pool
from cow_ethrpc import EthRpcClient
from cow_price_estimation import PriceEstimator
from cow_shared import AppDataRegistry, OrderValidator

MAINNET_CHAIN_ID = 1
MAINNET_SETTLEMENT = "0x9008D19f58AAbD9eD0D60971565AA8510560ab41"


@dataclass
class AppState:
    config: OrderbookConfig
    db_write: Postgres
    db_read: Postgres
    validator: OrderValidator
    app_data: AppDataRegistry
    price_estimator: PriceEstimator | None
    eth_client: EthRpcClient
    domain_separator: bytes


def settlement_address(config: OrderbookConfig) -> str:
    return config.shared.contracts.settlement or MAINNET_SETTLEMENT


def chain_id(config: OrderbookConfig) -> int:
    return config.shared.chain_id or MAINNET_CHAIN_ID


def domain_separator_bytes(config: OrderbookConfig) -> bytes:
    from cow_model import DomainSeparator

    return DomainSeparator.from_chain(chain_id(config), settlement_address(config)).value


async def build_state(config: OrderbookConfig) -> AppState:
    db_write = await create_pool(config.database)
    db_read = await Postgres.create_read(config.database)

    drivers = []
    if config.order_quoting:
        drivers = [(d.name, d.url) for d in config.order_quoting.price_estimation_drivers]

    return AppState(
        config=config,
        db_write=db_write,
        db_read=db_read,
        validator=OrderValidator(
            banned_users=set(config.banned_users.addresses),
            unsupported_tokens=set(config.unsupported_tokens),
        ),
        app_data=AppDataRegistry(),
        price_estimator=PriceEstimator(drivers) if drivers else None,
        eth_client=EthRpcClient(config.shared.node_url),
        domain_separator=domain_separator_bytes(config),
    )
