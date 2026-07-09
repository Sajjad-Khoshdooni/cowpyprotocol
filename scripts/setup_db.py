#!/usr/bin/env python3
"""Create cowprotocol DB and apply migrations via psql."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

DB_NAME = "cowprotocol"
MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "database" / "sql"


def main() -> None:
    user = os.environ.get("USER", "postgres")
    admin_dsn = f"postgresql://{user}@localhost/postgres"
    db_dsn = f"postgresql://{user}@localhost/{DB_NAME}"

    # Create database if missing
    subprocess.run(
        ["psql", admin_dsn, "-tc", f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'"],
        check=True,
        capture_output=True,
        text=True,
    )
    result = subprocess.run(
        ["psql", admin_dsn, "-tc", f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'"],
        capture_output=True,
        text=True,
    )
    if "1" not in result.stdout:
        subprocess.run(["psql", admin_dsn, "-c", f'CREATE DATABASE "{DB_NAME}"'], check=True)
        print(f"Created database {DB_NAME}")
    else:
        print(f"Database {DB_NAME} already exists")

    os.environ["DB_WRITE_URL"] = db_dsn
    os.environ["DB_READ_URL"] = db_dsn

    # Track migrations in schema_migrations
    subprocess.run(
        [
            "psql",
            db_dsn,
            "-c",
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                description TEXT NOT NULL,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """,
        ],
        check=True,
    )

    import re

    pattern = re.compile(r"^V(\d+)__(.+)\.sql$")
    files = sorted(
        (f for f in MIGRATIONS_DIR.glob("V*.sql") if pattern.match(f.name)),
        key=lambda f: int(pattern.match(f.name).group(1)),  # type: ignore[union-attr]
    )

    applied = subprocess.run(
        ["psql", db_dsn, "-tc", "SELECT version FROM schema_migrations ORDER BY version"],
        capture_output=True,
        text=True,
        check=True,
    )
    applied_versions = {int(v.strip()) for v in applied.stdout.splitlines() if v.strip().isdigit()}

    count = 0
    for migration_file in files:
        match = pattern.match(migration_file.name)
        if not match:
            continue
        version = int(match.group(1))
        description = match.group(2)
        if version in applied_versions:
            continue
        print(f"Applying {migration_file.name}...")
        subprocess.run(["psql", db_dsn, "-v", "ON_ERROR_STOP=1", "-f", str(migration_file)], check=True)
        subprocess.run(
            [
                "psql",
                db_dsn,
                "-c",
                f"INSERT INTO schema_migrations (version, description) VALUES ({version}, '{description}');",
            ],
            check=True,
        )
        count += 1

    print(f"Applied {count} new migrations from {MIGRATIONS_DIR}")


if __name__ == "__main__":
    main()
