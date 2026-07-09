"""E2E tests — port of crates/e2e."""

import time

import pytest
from cow_configs import OrderbookConfig
from cow_driver.app import create_app as create_driver_app
from cow_ethrpc import EthRpcClient
from cow_model import OrderCreation, OrderKind, compute_order_uid
from cow_orderbook.app import create_app as create_orderbook_app
from cow_orderbook.state import AppState, domain_separator_bytes
from cow_shared import AppDataRegistry, OrderValidator, SignatureValidator
from httpx import ASGITransport, AsyncClient

DOMAIN = bytes.fromhex("74e0b11bd18120612556bae4578cfd3a254d7e2495f543c569a92ff5794d9b09")
GPV2_OWNER = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
EIP712_SIGNATURE = (
    "0x59c0f5c151071c1320575f6da826a6c276525bbe733234bad1afb2879657d65d"
    "2afe6812746f4cc97f28f3a5dfdbfc7087511695d23da5e9792cd7ed6c9ddeb7"
    "1c"
)


@pytest.fixture
def orderbook_config() -> OrderbookConfig:
    return OrderbookConfig()


@pytest.fixture
def app_state(orderbook_config: OrderbookConfig) -> AppState:
    return AppState(
        config=orderbook_config,
        db_write=None,  # type: ignore[arg-type]
        db_read=None,  # type: ignore[arg-type]
        validator=OrderValidator(),
        app_data=AppDataRegistry(),
        price_estimator=None,
        eth_client=EthRpcClient("http://localhost:8545"),
        domain_separator=domain_separator_bytes(orderbook_config),
    )


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_orderbook_version(app_state: AppState) -> None:
    app = create_orderbook_app(app_state)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/version")
        assert response.status_code == 200
        assert "version" in response.json()


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_orderbook_ready(app_state: AppState) -> None:
    app = create_orderbook_app(app_state)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/ready")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_driver_healthz() -> None:
    app = create_driver_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/healthz")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_driver_solve() -> None:
    app = create_driver_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/solve", json={"id": 1, "orders": []})
        assert response.status_code == 200
        assert "solutions" in response.json()


@pytest.mark.e2e
def test_order_uid_matches_gpv2_contract_vector() -> None:
    """Order UID must match GPv2Signing.test.ts / model/order.rs vector."""
    order = OrderCreation(
        sellToken="0x0101010101010101010101010101010101010101",
        buyToken="0x0202020202020202020202020202020202020202",
        receiver="0x0303030303030303030303030303030303030303",
        sellAmount=0x0246DDF97976680000,
        buyAmount=0x0B98BC829A6F90000,
        validTo=0xFFFFFFFF,
        appData="0x0000000000000000000000000000000000000000000000000000000000000000",
        feeAmount=0x0DE0B6B3A7640000,
        kind=OrderKind.SELL,
        partiallyFillable=False,
        signingScheme="eip712",
        signature=EIP712_SIGNATURE,
        from_=GPV2_OWNER,
    )
    uid = compute_order_uid(order, DOMAIN, GPV2_OWNER)
    assert uid == (
        "0x0e45d31fd31b28c26031cdd81b35a8938b2ccca2cc425fcf440fd3bfed1eede9"
        "70997970c51812dc3a010c7d01b50e0d17dc79c8"
        "ffffffff"
    )


@pytest.mark.e2e
def test_eip712_signature_recovery_matches_gpv2_vector() -> None:
    order = OrderCreation(
        sellToken="0x0101010101010101010101010101010101010101",
        buyToken="0x0202020202020202020202020202020202020202",
        receiver="0x0303030303030303030303030303030303030303",
        sellAmount=0x0246DDF97976680000,
        buyAmount=0x0B98BC829A6F90000,
        validTo=0xFFFFFFFF,
        appData="0x0000000000000000000000000000000000000000000000000000000000000000",
        feeAmount=0x0DE0B6B3A7640000,
        kind=OrderKind.SELL,
        partiallyFillable=False,
        signingScheme="eip712",
        signature=EIP712_SIGNATURE,
        from_=GPV2_OWNER,
    )
    validator = SignatureValidator(DOMAIN)
    assert validator.validate_owner(order) == GPV2_OWNER


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_orderbook_rejects_expired_order(app_state: AppState) -> None:
    app = create_orderbook_app(app_state)
    transport = ASGITransport(app=app)
    expired = OrderCreation(
        sellToken="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        buyToken="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        sellAmount=1000,
        buyAmount=900,
        validTo=int(time.time()) - 60,
        appData="0x0000000000000000000000000000000000000000000000000000000000000000",
        feeAmount=10,
        kind=OrderKind.SELL,
        partiallyFillable=False,
        signingScheme="eip712",
        signature="0x" + "00" * 65,
        from_=GPV2_OWNER,
    )
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/orders", json=expired.model_dump(by_alias=True))
        assert response.status_code == 400
        assert response.json()["errorType"] == "ValidationError"
