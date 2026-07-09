help:
    @just --list

# Install all workspace dependencies
sync:
    uv sync --all-packages

# Create local DB and apply migrations
setup-db:
    uv run python scripts/setup_db.py

# Run unit tests
test-unit:
    uv run pytest packages/ tests/ -m "not postgres and not e2e" -v

# Run e2e tests
test-e2e:
    uv run pytest tests/e2e -m e2e -v

# Smoke test against running services
smoke-test:
    uv run python scripts/smoke_test.py

# Run orderbook (local config)
run-orderbook:
    #!/usr/bin/env bash
    export DB_WRITE_URL="postgresql://${USER}@localhost/cowprotocol"
    export DB_READ_URL="postgresql://${USER}@localhost/cowprotocol"
    uv run cow-orderbook --config configs/local-orderbook.toml --port 8080

# Run driver (for quotes)
run-driver:
    uv run cow-driver --config configs/local-orderbook.toml --addr 127.0.0.1:11088

# Lint
lint:
    uv run ruff check packages/ tests/ scripts/

# Format
fmt:
    uv run ruff format packages/ tests/ scripts/
