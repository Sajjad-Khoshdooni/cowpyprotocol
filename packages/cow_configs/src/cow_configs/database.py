"""Database pool configuration — port of configs/database.rs."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from cow_configs.deserialize_env import resolve_env_url, resolve_optional_env_url


class DatabasePoolConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    write_url: str = Field(default="postgresql://", alias="write-url")
    read_url: str | None = Field(default=None, alias="read-url")
    max_connections: int = Field(default=10, alias="db-max-connections")
    insert_batch_size: int = Field(default=500, alias="insert-batch-size")
    statement_timeout_seconds: int = Field(default=30, alias="statement-timeout")

    @field_validator("write_url", mode="before")
    @classmethod
    def resolve_write_url(cls, v: str) -> str:
        return resolve_env_url(v)

    @field_validator("read_url", mode="before")
    @classmethod
    def resolve_read_url(cls, v: str | None) -> str | None:
        return resolve_optional_env_url(v)

    def effective_read_url(self) -> str:
        return self.read_url or self.write_url

    def __repr__(self) -> str:
        return "DatabasePoolConfig(write_url=REDACTED, read_url=REDACTED)"
