"""NATS event bus — port of observe event bus + event-bus-dto."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EventType(str, Enum):
    QUOTE_REQUESTED = "QuoteRequested"
    QUOTE_COMPUTED = "QuoteComputed"
    PRICE_ESTIMATE = "PriceEstimate"


class EventBusMessage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    event_type: EventType = Field(alias="eventType")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    payload: dict[str, Any] = {}


def subject_for(chain_id: int, event_type: EventType) -> str:
    return f"event.{chain_id}.{event_type.value}"


class EventBusPublisher:
    """Publishes events to NATS JetStream."""

    def __init__(self, nc, chain_id: int) -> None:
        self._nc = nc
        self._chain_id = chain_id

    async def publish(self, event_type: EventType, payload: dict[str, Any]) -> None:
        msg = EventBusMessage(eventType=event_type, payload=payload)
        subject = subject_for(self._chain_id, event_type)
        await self._nc.publish(subject, json.dumps(msg.model_dump(mode="json")).encode())
