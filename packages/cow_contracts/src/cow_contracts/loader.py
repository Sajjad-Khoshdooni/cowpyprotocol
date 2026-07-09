"""ABI loader from services/contracts/artifacts/."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from web3 import AsyncWeb3
from web3.contract import AsyncContract

ARTIFACTS_DIR = Path(__file__).resolve().parents[5] / "services" / "contracts" / "artifacts"


@lru_cache(maxsize=128)
def get_abi(contract_name: str) -> list:
    """Load ABI from artifact JSON file."""
    artifact_path = ARTIFACTS_DIR / f"{contract_name}.json"
    if not artifact_path.exists():
        raise FileNotFoundError(f"contract artifact not found: {artifact_path}")
    data = json.loads(artifact_path.read_text())
    return data["abi"]


def load_contract(w3: AsyncWeb3, contract_name: str, address: str) -> AsyncContract:
    """Create a web3.py contract instance from artifact ABI."""
    abi = get_abi(contract_name)
    return w3.eth.contract(address=w3.to_checksum_address(address), abi=abi)
