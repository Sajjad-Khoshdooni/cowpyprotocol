# What I learned by porting CoW Protocol services architecture to Python

This note captures lessons from building **cowpyprotocol** — an experimental Python architecture port of the Rust `services/` workspace (~40 crates, 7 binaries). The goal was not a line-by-line rewrite but to understand whether the same system shape works in Python.

## 1. The hard parts are cryptographic, not HTTP

Most of the Rust codebase is orchestration: HTTP handlers, database queries, RPC calls, background loops. In Python those map cleanly to FastAPI, asyncpg, and asyncio. What does **not** map trivially is the boundary with Ethereum:

- **EIP-712 struct hashing** for `GPv2Order` uses a fixed 416-byte in-memory layout in Rust. Porting it required reading `order.rs` byte-for-byte, not re-deriving from the JSON schema.
- **Order UIDs** are `keccak256(EIP712(domain, structHash)) ‖ owner ‖ validTo` — 56 bytes, not a database UUID.
- **Signature recovery** must normalize `v` (0/1 → 27/28) exactly as Solidity's `ecover` expects.

Once these three pieces match [GPv2Signing.test.ts](https://github.com/cowprotocol/contracts/blob/v1.1.2/test/GPv2Signing.test.ts), the orderbook can accept real signed orders. Everything else is plumbing.

## 2. Crate boundaries become package boundaries — mostly

Rust's workspace enforces dependency direction: `model` has no I/O, `database` depends on `model`, services depend on both. The Python port mirrors this with 21 `cow_*` packages in a uv workspace.

What changed:

| Rust | Python | Lesson |
|------|--------|--------|
| `anyhow` / `thiserror` | plain `Exception` subclasses | Fine for a prototype; production would want structured errors |
| `sqlx` compile-time SQL | asyncpg + string queries | Lose compile-time checks; gain simpler async |
| `alloy` / `web3` split | `eth_account` + `web3.py` | EIP-712 domain separator via `hash_domain` is the right abstraction |
| Tokio tasks | `asyncio` + uvicorn | Event-loop sharing between pool init and server required care |

The **package graph** was the best investment: it forces you to port `model` and `configs` before services, which matches how the Rust repo evolved.

## 3. Database compatibility is a symlink away

CoW's PostgreSQL schema is defined in 111 Flyway-style migrations under `services/database/sql/`. Rather than re-specify the schema in Python, cowpyprotocol symlinks `database/` to the Rust tree and runs migrations with `psql`.

This means:

- Python inserts use the same `orders` table shape as production.
- CI can sparse-checkout only `database/` from `cowprotocol/services`.
- asyncpg cannot run multi-statement migration files — `psql` is the right tool.

## 4. Stubs are useful if labeled honestly

A full port of `liquidity-sources` alone is thousands of lines. The honest approach for an architecture port:

1. Implement **one vertical slice deeply** (order UID + signature recovery).
2. Scaffold HTTP routes so the API surface is discoverable.
3. Publish a **status matrix** so readers know what is real vs placeholder.

Without the matrix, a repo with 21 packages looks "done" when most `/solve` paths return `[]`.

## 5. CI assumptions drift from local monorepos

Three bugs that only show up when the repo stands alone:

- **Branch name**: local `master`, workflow triggers on `main`.
- **Working directory**: workflow assumed `cowpyprotocol/` subdirectory; repo root *is* cowpyprotocol.
- **Hidden failures**: `pytest ... || true` on database tests masks broken migrations.

Fixing these early prevents "green CI, red reality."

## 6. What I would do next

If this were moving toward production:

1. Port **order validation** fully (balances, hooks, app-data parsing).
2. Wire **autopilot → driver → solver** with a real baseline solver path.
3. Add **property tests** that round-trip orders through Rust `model` and Python `cow_model` via shared JSON fixtures.
4. Run **contract tests** against a local Anvil fork with the real settlement contract.

For now, the port's value is architectural: it proves the CoW services decomposition (model / database / orderbook / autopilot / driver / solvers) is language-agnostic, and it surfaces exactly which layers are crypto-heavy vs orchestration-heavy.

## Further reading

- [CoW Protocol services (Rust)](https://github.com/cowprotocol/services)
- [GPv2 settlement contracts](https://github.com/cowprotocol/contracts)
- [cowpyprotocol README](../README.md) — status matrix and quick start
