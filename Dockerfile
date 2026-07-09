FROM python:3.11-slim AS builder

WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
COPY packages/ packages/

RUN uv sync --frozen --no-dev

FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/packages /app/packages
COPY pyproject.toml .

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8080

CMD ["cow-orderbook", "--config", "/config/orderbook.toml"]
