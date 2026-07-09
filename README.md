# cowpyprotocol

> **Vibecoded.** This project was scaffolded rapidly with AI assistance as an **experimental Python architecture port** of the [CoW Protocol services](https://github.com/cowprotocol/services) backend. It is **not production-ready** — treat it as a working prototype and learning exercise, not an audited drop-in replacement.

An experimental Python architecture port of the CoW Protocol off-chain stack: orderbook, autopilot, driver, solvers, and supporting libraries. The goal is API/schema/config compatibility with the Rust [`services/`](../services/) workspace, but many code paths are still stubs or simplified.

## Status matrix

| Area | Status | Notes |
|------|--------|-------|
| **Order UID (EIP-712)** | Implemented | Matches GPv2Signing.test.ts vectors |
| **EIP-712 / eth_sign recovery** | Implemented | Off-chain ECDSA recovery for order creation |
| **Order validation** | Partial | Expiry, tokens, amounts; no full on-chain balance checks |
| **Orderbook HTTP API** | Partial | Routes exist; many return stubs |
| **PostgreSQL layer** | Partial | Pool + core queries; not all Rust queries ported |
| **TOML configs** | Implemented | `%ENV_VAR%` substitution, playground-compatible shape |
| **Driver `/solve`** | Stub | Returns empty solutions |
| **Solver engines** | Stub | Baseline skeleton only |
| **Price estimation** | Stub | HTTP driver proxy, no real routing |
| **Liquidity sources** | Not implemented | Rust crate is ~12k lines |
| **Autopilot auction loop** | Stub | No settlement submission |
| **On-chain event indexing** | Not implemented | |
| **EIP-1271 / pre-sign validation** | Not implemented | Skippable via config flag |
| **Refunder / pool indexer / Solana** | Stub | CLI entry points only |
| **Contract ABIs** | Partial | Loaded from sibling `services/contracts/` when present |
| **Observability (NATS, tracing)** | Partial | Metrics endpoint; event bus not wired end-to-end |
| **CI / Docker** | Implemented | Tests on `master`/`main`; migrations fetched in CI |

Legend: **Implemented** = behavior verified against Rust/contracts tests · **Partial** = structure exists, behavior incomplete · **Stub** = compiles and responds, no real logic · **Not implemented** = missing or placeholder only

## What works today

- **Order UID computation** and **EIP-712 signature recovery** (verified against GPv2 contract test vectors)
- **Orderbook** HTTP API on FastAPI (`/api/v1/*`, `/api/v2/*`)
- **Driver** and **solver** skeletons (`/solve`, `/quote`, `/settle`)
- **PostgreSQL** via asyncpg, reusing Rust SQL migrations (`database/` → `../services/database/`)
- **TOML configs** with `%ENV_VAR%` substitution (same format as Rust)
- Unit tests, e2e tests, postgres integration tests, and a smoke-test script

## Architecture

```
User → orderbook → PostgreSQL
              ↓
autopilot (auction loop) → drivers → solvers
              ↓
driver simulates + submits → GPv2Settlement on-chain
              ↓
autopilot indexes events → PostgreSQL
```

See also: [What I learned by porting CoW Protocol services architecture to Python](docs/ARCHITECTURE.md).

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- PostgreSQL (local or Docker)
- Rust `services/` repo checked out next to this directory (for migrations & ABIs)

## Quick start

```bash
# 1. Install dependencies
uv sync --all-packages

# 2. Create database and run migrations
just setup-db

# 3. Start services (two terminals)
just run-orderbook   # http://127.0.0.1:8080
just run-driver      # http://127.0.0.1:11088

# 4. Verify
just smoke-test      # expect 7/7 passed
just test-unit       # unit + e2e (no live DB)
```

## Example API calls

```bash
# Health
curl -s http://127.0.0.1:8080/api/v1/version | jq
curl -s http://127.0.0.1:8080/api/v1/ready | jq

# Quote (requires driver on :11088)
curl -s -X POST http://127.0.0.1:8080/api/v1/quote \
  -H 'Content-Type: application/json' \
  -d '{
    "sellToken": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "buyToken": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "kind": "sell",
    "sellAmountBeforeFee": "1000000000000000000"
  }' | jq
```

> **Tip:** In zsh, don't use `UID=` for order UIDs — it's a reserved variable. Use `ORDER_UID=` instead.

## Project layout

```
cowpyprotocol/
├── packages/           # 21 Python packages (uv workspace)
│   ├── cow_model/      # Domain types, order UID, EIP-712
│   ├── cow_configs/    # TOML configuration
│   ├── cow_database/   # PostgreSQL layer
│   ├── cow_orderbook/  # HTTP API service
│   ├── cow_driver/     # Driver service
│   ├── cow_solvers/    # Solver engines
│   └── ...
├── configs/            # Local dev TOML configs
├── scripts/            # setup_db.py, smoke_test.py
├── tests/e2e/          # Integration tests
├── tests/integration/  # PostgreSQL tests (@pytest.mark.postgres)
├── docs/               # Architecture notes
├── database/           # Symlink → ../services/database/
├── Justfile            # Task runner
└── docker-compose.yaml # Optional Postgres overlay
```

## Development

```bash
just sync          # install deps
just lint          # ruff check
just fmt           # ruff format
just test-unit     # pytest (no DB required)
just test-e2e      # in-process API + crypto tests
just smoke-test    # live HTTP checks (services must be running)
```

Postgres integration tests require `DB_WRITE_URL` and applied migrations:

```bash
export DB_WRITE_URL=postgresql://localhost/cowprotocol
export DB_READ_URL=postgresql://localhost/cowprotocol
uv run pytest -m postgres -v
```

## License

Same as the upstream CoW Protocol services (MIT OR Apache-2.0).
