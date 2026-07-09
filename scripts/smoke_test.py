#!/usr/bin/env python3
"""Smoke test: call orderbook APIs as a user would."""

from __future__ import annotations

import sys

import httpx

BASE = "http://127.0.0.1:8080"


def main() -> int:
    results: list[tuple[str, bool, str]] = []

    with httpx.Client(base_url=BASE, timeout=10.0) as client:
        try:
            r = client.get("/api/v1/version")
            ok = r.status_code == 200 and "version" in r.json()
            results.append(("GET /api/v1/version", ok, f"{r.status_code} {r.text[:120]}"))
        except Exception as e:
            results.append(("GET /api/v1/version", False, str(e)))

        try:
            r = client.get("/api/v1/ready")
            ok = r.status_code == 200 and r.json().get("status") == "ok"
            results.append(("GET /api/v1/ready", ok, f"{r.status_code} {r.text}"))
        except Exception as e:
            results.append(("GET /api/v1/ready", False, str(e)))

        try:
            r = client.get("/api/v1/auction")
            ok = r.status_code == 200
            results.append(("GET /api/v1/auction", ok, f"{r.status_code} {r.text[:200]}"))
        except Exception as e:
            results.append(("GET /api/v1/auction", False, str(e)))

        quote_body = {
            "sellToken": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "buyToken": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "kind": "sell",
            "sellAmountBeforeFee": "1000000000000000000",
            "from": "0x0000000000000000000000000000000000000001",
        }
        try:
            r = client.post("/api/v1/quote", json=quote_body)
            ok = r.status_code in (200, 503)
            results.append(("POST /api/v1/quote", ok, f"{r.status_code} {r.text[:200]}"))
        except Exception as e:
            results.append(("POST /api/v1/quote", False, str(e)))

        import time

        order_body = {
            "sellToken": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "buyToken": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "sellAmount": "1000000000000000000",
            "buyAmount": "1000000",
            "validTo": int(time.time()) + 3600,
            "appData": "0x0000000000000000000000000000000000000000000000000000000000000000",
            "feeAmount": "1000000000000000",
            "kind": "sell",
            "partiallyFillable": False,
            "signingScheme": "eip712",
            "signature": "0x" + "00" * 65,
            "from": "0x0000000000000000000000000000000000000001",
        }
        try:
            r = client.post("/api/v1/orders", json=order_body)
            ok = r.status_code == 201 and "uid" in r.json()
            results.append(("POST /api/v1/orders", ok, f"{r.status_code} {r.text[:200]}"))
            if ok:
                uid = r.json()["uid"]
                r2 = client.get(f"/api/v1/orders/{uid}")
                results.append((f"GET /api/v1/orders/{{uid}}", r2.status_code in (200, 404), f"{r2.status_code}"))
        except Exception as e:
            results.append(("POST /api/v1/orders", False, str(e)))

        try:
            r = client.get("/metrics")
            results.append(("GET /metrics", r.status_code == 200, f"{r.status_code} len={len(r.text)}"))
        except Exception as e:
            results.append(("GET /metrics", False, str(e)))

    print("\n=== CoW Orderbook Smoke Test ===\n")
    passed = sum(1 for _, ok, _ in results if ok)
    for name, ok, detail in results:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {name}")
        print(f"         {detail}\n")

    print(f"Result: {passed}/{len(results)} checks passed\n")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
