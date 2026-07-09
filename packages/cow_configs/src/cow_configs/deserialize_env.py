"""Environment variable substitution — port of configs/deserialize_env.rs."""

from __future__ import annotations

import os
from urllib.parse import urlparse

ENV_VAR_PREFIX = "%"


def resolve_env_string(value: str) -> str:
    """Resolve %ENV_VAR_NAME to environment variable value."""
    if value.startswith(ENV_VAR_PREFIX):
        env_name = value[1:]
        if env_name not in os.environ:
            raise ValueError(f"environment variable {env_name!r} not found")
        return os.environ[env_name]
    return value


def resolve_optional_env_string(value: str | None) -> str | None:
    if value is None:
        return None
    if value.startswith(ENV_VAR_PREFIX):
        env_name = value[1:]
        return os.environ.get(env_name)
    return value


def resolve_env_url(value: str) -> str:
    resolved = resolve_env_string(value)
    parsed = urlparse(resolved)
    if not parsed.scheme:
        raise ValueError(f"invalid URL: {resolved!r}")
    return resolved


def resolve_optional_env_url(value: str | None) -> str | None:
    if value is None:
        return None
    if value.startswith(ENV_VAR_PREFIX):
        env_name = value[1:]
        raw = os.environ.get(env_name)
        if raw is None:
            return None
        return resolve_env_url(raw)
    return resolve_env_url(value)
