"""TOML configuration loader."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def load_toml_config(path: str | Path, model: type[T]) -> T:
    """Load and parse a TOML config file into a Pydantic model."""
    data = tomllib.loads(Path(path).read_text())
    return model.model_validate(data)
