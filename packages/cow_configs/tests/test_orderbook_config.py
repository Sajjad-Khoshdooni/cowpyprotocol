"""Tests for configuration loading."""

from pathlib import Path

import pytest
from cow_configs import OrderbookConfig, load_toml_config

PLAYGROUND_CONFIG = (
    Path(__file__).resolve().parents[4] / "services" / "playground" / "configs" / "orderbook.toml"
)


def test_load_playground_orderbook_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DB_WRITE_URL", "postgresql://write@localhost/cow")
    monkeypatch.setenv("DB_READ_URL", "postgresql://read@localhost/cow")

    config = load_toml_config(PLAYGROUND_CONFIG, OrderbookConfig)

    assert config.bind_address == "0.0.0.0:80"
    assert config.database.write_url == "postgresql://write@localhost/cow"
    assert config.database.read_url == "postgresql://read@localhost/cow"
    assert config.eip1271_skip_creation_validation is True
    assert config.shared.node_url == "http://chain:8545"
