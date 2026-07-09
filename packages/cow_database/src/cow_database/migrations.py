"""SQL migration runner — applies services/database/sql/ migrations."""

from __future__ import annotations

import re
from pathlib import Path

import asyncpg

MIGRATION_PATTERN = re.compile(r"^V(\d+)__(.+)\.sql$")


def _split_sql_statements(sql: str) -> list[str]:
    """Split SQL file into individual statements (asyncpg runs one at a time)."""
    statements: list[str] = []
    current: list[str] = []
    for line in sql.splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        current.append(line)
        if stripped.endswith(";"):
            stmt = "\n".join(current).strip().rstrip(";").strip()
            if stmt:
                statements.append(stmt)
            current = []
    tail = "\n".join(current).strip().rstrip(";").strip()
    if tail:
        statements.append(tail)
    return statements


async def apply_migrations(pool: asyncpg.Pool, migrations_dir: str | Path) -> int:
    """Apply pending Flyway-style SQL migrations. Returns count applied."""
    migrations_path = Path(migrations_dir)
    if not migrations_path.exists():
        raise FileNotFoundError(f"migrations directory not found: {migrations_path}")

    async with pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                description TEXT NOT NULL,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        applied = await conn.fetch("SELECT version FROM schema_migrations ORDER BY version")
        applied_versions = {row["version"] for row in applied}

        migration_files = sorted(
            (f for f in migrations_path.glob("V*.sql") if MIGRATION_PATTERN.match(f.name)),
            key=lambda f: int(MIGRATION_PATTERN.match(f.name).group(1)),  # type: ignore[union-attr]
        )

        count = 0
        for migration_file in migration_files:
            match = MIGRATION_PATTERN.match(migration_file.name)
            if not match:
                continue
            version = int(match.group(1))
            description = match.group(2)
            if version in applied_versions:
                continue
            sql = migration_file.read_text()
            async with conn.transaction():
                for statement in _split_sql_statements(sql):
                    await conn.execute(statement)
                await conn.execute(
                    "INSERT INTO schema_migrations (version, description) VALUES ($1, $2)",
                    version,
                    description,
                )
            count += 1
        return count
