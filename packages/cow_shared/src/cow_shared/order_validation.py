"""Order validation — port of order-validation + shared order validation."""

from __future__ import annotations

from datetime import UTC, datetime

from cow_model import OrderCreation, OrderKind


class ValidationError(Exception):
    pass


class OrderValidator:
    """Validates orders before persistence."""

    def __init__(
        self,
        *,
        max_validity_period_seconds: int = 365 * 24 * 3600,
        banned_users: set[str] | None = None,
        unsupported_tokens: set[str] | None = None,
    ) -> None:
        self._max_validity = max_validity_period_seconds
        self._banned_users = banned_users or set()
        self._unsupported_tokens = unsupported_tokens or set()

    def validate(self, order: OrderCreation) -> None:
        now = int(datetime.now(UTC).timestamp())
        if order.valid_to <= now:
            raise ValidationError("order already expired")
        if order.valid_to - now > self._max_validity:
            raise ValidationError("order validity period too long")
        if order.sell_token == order.buy_token:
            raise ValidationError("sell and buy tokens must differ")
        if order.from_ and order.from_.lower() in {u.lower() for u in self._banned_users}:
            raise ValidationError("user is banned")
        for token in (order.sell_token, order.buy_token):
            if token.lower() in {t.lower() for t in self._unsupported_tokens}:
                raise ValidationError(f"token {token} is not supported")
        if order.kind == OrderKind.SELL and order.sell_amount <= 0:
            raise ValidationError("sell amount must be positive")
        if order.kind == OrderKind.BUY and order.buy_amount <= 0:
            raise ValidationError("buy amount must be positive")
