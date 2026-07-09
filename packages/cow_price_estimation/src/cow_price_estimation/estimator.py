"""Price estimation — port of price-estimation crate."""

from __future__ import annotations

from dataclasses import dataclass

import httpx
from cow_model import QuoteRequest


class PriceEstimationError(Exception):
    pass


@dataclass
class PriceEstimate:
    sell_amount: int
    buy_amount: int
    fee_amount: int


class PriceEstimator:
    """Estimates prices via configured driver endpoints."""

    def __init__(self, drivers: list[tuple[str, str]]) -> None:
        self._drivers = drivers  # (name, url) pairs

    async def estimate(self, request: QuoteRequest) -> PriceEstimate:
        errors: list[str] = []
        async with httpx.AsyncClient(timeout=5.0) as client:
            for name, url in self._drivers:
                try:
                    response = await client.get(
                        f"{url.rstrip('/')}/quote",
                        params={
                            "sellToken": request.sell_token,
                            "buyToken": request.buy_token,
                            "kind": request.kind.value,
                            "sellAmount": str(request.sell_amount_before_fee or 0),
                            "buyAmount": str(request.buy_amount_after_fee or 0),
                        },
                    )
                    response.raise_for_status()
                    data = response.json()
                    return PriceEstimate(
                        sell_amount=int(data.get("sellAmount", 0)),
                        buy_amount=int(data.get("buyAmount", 0)),
                        fee_amount=int(data.get("feeAmount", 0)),
                    )
                except Exception as e:
                    errors.append(f"{name}: {e}")
        raise PriceEstimationError("; ".join(errors) or "no drivers configured")
