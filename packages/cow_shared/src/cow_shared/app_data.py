"""App data registry — port of app-data crate."""

from __future__ import annotations

import hashlib
import json
from typing import Any


class AppDataRegistry:
    """Stores and retrieves order app data by hash."""

    def __init__(self) -> None:
        self._cache: dict[str, dict[str, Any]] = {}

    @staticmethod
    def hash_app_data(app_data: str | dict[str, Any]) -> str:
        if isinstance(app_data, dict):
            content = json.dumps(app_data, separators=(",", ":"), sort_keys=True)
        else:
            content = app_data
        digest = hashlib.sha256(content.encode()).hexdigest()
        return "0x" + digest

    async def get(self, app_data_hash: str) -> dict[str, Any] | None:
        return self._cache.get(app_data_hash.lower())

    async def put(self, app_data_hash: str, data: dict[str, Any]) -> None:
        self._cache[app_data_hash.lower()] = data
