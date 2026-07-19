"""SQLite connection helpers for the modular JEPA Site Manager layer."""

import sqlite3
from pathlib import Path

from database.db import DB_PATH, get_connection as base_get_connection


def get_connection() -> sqlite3.Connection:
    """Return the same SQLite connection used by the existing app."""
    ensure_schema()
    return base_get_connection()


def ensure_schema() -> None:
    """Run the modular schema extensions and migration scripts on top of the existing database."""
    schema_path = Path(__file__).with_name("schema.sql")
    migrations_dir = Path(__file__).resolve().parent / "migrations"

    with base_get_connection() as conn:
        conn.executescript(schema_path.read_text(encoding="utf-8"))

        if migrations_dir.exists():
            migration_files = sorted(migrations_dir.glob("*.sql"))
            for migration_path in migration_files:
                conn.executescript(migration_path.read_text(encoding="utf-8"))

        conn.commit()
