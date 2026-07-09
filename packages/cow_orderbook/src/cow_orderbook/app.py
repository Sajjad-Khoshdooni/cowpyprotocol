"""FastAPI application — port of orderbook/api.rs routes."""

from __future__ import annotations

import json
from typing import Any

from cow_model import OrderCreation, QuoteRequest, compute_order_uid
from cow_observe.metrics import metrics_endpoint
from cow_shared import SignatureValidator, ValidationError
from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse

from cow_orderbook.state import AppState, settlement_address


def create_app(state: AppState) -> FastAPI:
    app = FastAPI(title="CoW Protocol Orderbook", version="0.1.0")
    app.state.cow = state

    @app.exception_handler(ValidationError)
    async def validation_error_handler(_request: Request, exc: ValidationError) -> Response:
        return JSONResponse(status_code=400, content={"errorType": "ValidationError", "description": str(exc)})

    # --- Health & metadata ---
    @app.get("/api/v1/version")
    async def version() -> dict[str, str]:
        return {"version": "0.1.0", "gitCommit": "cowpyprotocol"}

    @app.get("/api/v1/ready")
    async def ready() -> dict[str, str]:
        return {"status": "ok"}

    # --- Quotes ---
    @app.post("/api/v1/quote")
    async def post_quote(request: QuoteRequest) -> dict[str, Any]:
        if not state.price_estimator:
            raise HTTPException(503, "price estimation not configured")
        estimate = await state.price_estimator.estimate(request)
        return {
            "quote": {
                "sellToken": request.sell_token,
                "buyToken": request.buy_token,
                "sellAmount": str(estimate.sell_amount),
                "buyAmount": str(estimate.buy_amount),
                "feeAmount": str(estimate.fee_amount),
                "kind": request.kind.value,
            }
        }

    @app.post("/api/v1/quote/stream")
    async def post_quote_stream(request: QuoteRequest):
        async def event_generator():
            if state.price_estimator:
                estimate = await state.price_estimator.estimate(request)
                yield {
                    "event": "quote",
                    "data": json.dumps(
                        {
                            "sellAmount": str(estimate.sell_amount),
                            "buyAmount": str(estimate.buy_amount),
                            "feeAmount": str(estimate.fee_amount),
                        }
                    ),
                }
            yield {"event": "finished", "data": "{}"}

        return EventSourceResponse(event_generator())

    # --- Orders ---
    @app.post("/api/v1/orders", status_code=201)
    async def post_order(order: OrderCreation) -> dict[str, str]:
        state.validator.validate(order)

        signer_validator = SignatureValidator(state.domain_separator)
        try:
            owner = signer_validator.validate_owner(order)
        except (ValueError, NotImplementedError) as exc:
            if state.config.eip1271_skip_creation_validation and order.from_:
                owner = order.from_
            else:
                raise HTTPException(
                    400,
                    detail={"errorType": "InvalidSignature", "description": str(exc)},
                ) from exc

        uid = compute_order_uid(order, state.domain_separator, owner)
        settlement = settlement_address(state.config)
        async with state.db_write.transaction() as conn:
            from cow_database.orders import insert_order

            await insert_order(
                conn,
                {
                    "uid": uid,
                    "owner": owner,
                    "sell_token": order.sell_token,
                    "buy_token": order.buy_token,
                    "receiver": order.receiver,
                    "sell_amount": order.sell_amount,
                    "buy_amount": order.buy_amount,
                    "valid_to": order.valid_to,
                    "app_data": order.app_data,
                    "fee_amount": order.fee_amount,
                    "kind": order.kind.value,
                    "partially_fillable": order.partially_fillable,
                    "signature": order.signature,
                    "signing_scheme": order.signing_scheme,
                    "settlement_contract": settlement,
                    "sell_token_balance": order.sell_token_balance.value,
                    "buy_token_balance": order.buy_token_balance.value,
                    "class": "market",
                },
            )
        return {"uid": uid}

    @app.get("/api/v1/orders/{uid}")
    async def get_order(uid: str) -> dict[str, Any]:
        async with state.db_read.transaction() as conn:
            from cow_database.orders import get_order_by_uid

            row = await get_order_by_uid(conn, uid)
            if not row:
                raise HTTPException(404, "order not found")
            return {"uid": uid}

    @app.delete("/api/v1/orders/{uid}")
    async def cancel_order(uid: str) -> Response:
        return Response(status_code=204)

    @app.delete("/api/v1/orders")
    async def cancel_orders() -> Response:
        return Response(status_code=204)

    @app.get("/api/v1/orders/{uid}/status")
    async def get_order_status(uid: str) -> dict[str, str]:
        return {"type": "open"}

    @app.post("/api/v1/orders/by_uids")
    async def get_orders_by_uids(uids: list[str]) -> list[dict[str, Any]]:
        return [{"uid": uid} for uid in uids]

    @app.get("/api/v1/account/{owner}/orders")
    async def get_user_orders(
        owner: str,
        offset: int = Query(0),
        limit: int = Query(10),
    ) -> list[dict[str, Any]]:
        async with state.db_read.transaction() as conn:
            from cow_database.orders import get_orders_by_owner

            rows = await get_orders_by_owner(conn, owner, offset, limit)
            return [{"uid": "0x" + row["uid"].hex()} for row in rows]

    # --- Auction ---
    @app.get("/api/v1/auction")
    async def get_auction() -> dict[str, Any]:
        async with state.db_read.transaction() as conn:
            from cow_database.auction import get_current_auction

            auction = await get_current_auction(conn)
            if not auction:
                return {"id": None, "orders": []}
            payload = auction["json"] or {}
            if isinstance(payload, str):
                payload = json.loads(payload)
            return {"id": auction["id"], **payload}

    # --- Trades ---
    @app.get("/api/v1/trades")
    async def get_trades(
        owner: str | None = None,
        order_uid: str | None = Query(None, alias="orderUid"),
    ) -> list[dict[str, Any]]:
        return []

    @app.get("/api/v2/trades")
    async def get_trades_v2(
        owner: str | None = None,
        order_uid: str | None = Query(None, alias="orderUid"),
    ) -> list[dict[str, Any]]:
        return []

    # --- Solver competition ---
    @app.get("/api/v2/solver_competition/{auction_id}")
    async def get_solver_competition(auction_id: int) -> dict[str, Any]:
        return {"auctionId": auction_id, "solutions": []}

    @app.get("/api/v2/solver_competition/by_tx/{tx_hash}")
    async def get_solver_competition_by_tx(tx_hash: str) -> dict[str, Any]:
        return {"transactionHash": tx_hash, "solutions": []}

    # --- App data ---
    @app.get("/api/v1/app_data/{app_data_hash}")
    async def get_app_data(app_data_hash: str) -> dict[str, Any]:
        data = await state.app_data.get(app_data_hash)
        if not data:
            raise HTTPException(404, "app data not found")
        return data

    @app.put("/api/v1/app_data/{app_data_hash}")
    async def put_app_data(app_data_hash: str, body: dict[str, Any]) -> Response:
        await state.app_data.put(app_data_hash, body)
        return Response(status_code=204)

    # --- Token info ---
    @app.get("/api/v1/token/{token}/metadata")
    async def get_token_metadata(token: str) -> dict[str, Any]:
        return {"address": token, "symbol": "UNKNOWN", "decimals": 18}

    @app.get("/api/v1/token/{token}/native_price")
    async def get_native_price(token: str) -> dict[str, str]:
        return {"price": "0"}

    # --- Misc ---
    @app.get("/api/v1/transactions/{tx_hash}/orders")
    async def get_orders_by_tx(tx_hash: str) -> list[dict[str, Any]]:
        return []

    @app.get("/api/v1/users/{user}/total_surplus")
    async def get_total_surplus(user: str) -> dict[str, str]:
        return {"totalSurplus": "0"}

    # --- Metrics ---
    @app.get("/metrics")
    async def metrics() -> Response:
        content, content_type = metrics_endpoint()
        return Response(content=content, media_type=content_type)

    return app
