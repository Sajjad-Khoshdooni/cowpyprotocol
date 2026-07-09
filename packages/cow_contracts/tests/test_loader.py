"""Tests for contract ABI loading."""

import pytest
from cow_contracts.loader import ARTIFACTS_DIR, get_abi


@pytest.mark.skipif(not ARTIFACTS_DIR.exists(), reason="services/contracts artifacts not available")
def test_artifacts_dir_exists() -> None:
    assert ARTIFACTS_DIR.exists(), f"artifacts dir not found: {ARTIFACTS_DIR}"


@pytest.mark.skipif(not ARTIFACTS_DIR.exists(), reason="services/contracts artifacts not available")
def test_load_gpv2_settlement_abi() -> None:
    abi = get_abi("GPv2Settlement")
    assert isinstance(abi, list)
    assert len(abi) > 0
    assert any(item.get("type") == "function" for item in abi)
