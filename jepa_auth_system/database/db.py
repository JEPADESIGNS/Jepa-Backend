"""
database/db.py — Database connection, initialization, and migration.
"""
import os
import sqlite3
from pathlib import Path

# All persistent data lives under ~/.jepa_auth so the app is self-contained
APP_DIR = Path.home() / ".jepa_auth"
DB_PATH = APP_DIR / "data" / "jepa_auth.db"
PROFILE_PICS_DIR = APP_DIR / "profile_pics"
ALLOWED_ROLES = (
    "super_admin",
    "admin",
    "contractor",
    "project_manager",
    "site_engineer",
    "store_keeper",
    "equipment_officer",
    "client",
    "consultant",
)


def _ensure_dirs():
    os.makedirs(DB_PATH.parent, exist_ok=True)
    os.makedirs(PROFILE_PICS_DIR, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    """Return a new SQLite connection with foreign-key enforcement enabled."""
    _ensure_dirs()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    """Return True when a table exists in the current database."""
    return (
        conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        ).fetchone()
        is not None
    )


def _delete_user_related_rows(conn: sqlite3.Connection, user_ids: list[int]) -> None:
    """Remove dependent rows for legacy users before deleting the user accounts."""
    if not user_ids:
        return

    cleanup_targets = (
        ("otp_codes", "user_id"),
        ("notifications", "user_id"),
        ("logs", "user_id"),
        ("projects", "created_by"),
        ("sites", "responsible_user_id"),
        ("tasks", "assigned_user_id"),
        ("site_reports", "created_by"),
        ("materials", "created_by"),
    )

    for table_name, column_name in cleanup_targets:
        if not _table_exists(conn, table_name):
            continue

        columns = [row[1] for row in conn.execute(f"PRAGMA table_info({table_name})")]
        if column_name not in columns:
            continue

        placeholders = ",".join("?" for _ in user_ids)
        conn.execute(
            f"DELETE FROM {table_name} WHERE {column_name} IN ({placeholders})",
            user_ids,
        )


def _prune_disallowed_roles(conn: sqlite3.Connection) -> int:
    """Remove any legacy accounts that are not part of the approved role set."""
    placeholders = ",".join("?" for _ in ALLOWED_ROLES)

    legacy_users = conn.execute(
        "SELECT id FROM users WHERE role NOT IN (" + placeholders + ")",
        ALLOWED_ROLES,
    ).fetchall()

    legacy_ids = [row[0] for row in legacy_users]
    _delete_user_related_rows(conn, legacy_ids)

    deleted = conn.execute(
        "DELETE FROM users WHERE role NOT IN (" + placeholders + ")",
        ALLOWED_ROLES,
    ).rowcount
    return deleted


def init_db():
    """Create all tables from schema.sql if they do not already exist."""
    _ensure_dirs()
    schema_path = Path(__file__).resolve().parent / "schema.sql"
    with get_connection() as conn:
        if schema_path.exists():
            conn.executescript(schema_path.read_text())
        else:
            _create_tables_inline(conn)
        _run_migrations(conn)
        _prune_disallowed_roles(conn)
        conn.commit()


def _create_tables_inline(conn: sqlite3.Connection):
    """Fallback table creation if schema.sql is missing."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            username            TEXT UNIQUE NOT NULL,
            email               TEXT UNIQUE NOT NULL,
            phone               TEXT UNIQUE NOT NULL,
            password_hash       TEXT NOT NULL,
            role                TEXT NOT NULL DEFAULT 'user',
            status              TEXT NOT NULL DEFAULT 'active',
            profile_pic         TEXT DEFAULT 'assets/default_avatar.png',
            full_name           TEXT,
            country_code        TEXT DEFAULT '+256',
            gender              TEXT,
            dob                 TEXT,
            bio                 TEXT,
            security_question   TEXT,
            security_answer_hash TEXT,
            recovery_code       TEXT UNIQUE,
            theme               TEXT NOT NULL DEFAULT 'dark',
            totp_secret         TEXT,
            created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at          DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_id     INTEGER,
            username    TEXT,
            action      TEXT NOT NULL,
            ip_address  TEXT,
            details     TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)


def _run_migrations(conn: sqlite3.Connection):
    """Add any columns that might be missing from an older database."""
    migrations = [
        ("users", "username",             "TEXT"),
        ("users", "phone",                "TEXT"),
        ("users", "password_hash",        "TEXT"),
        ("users", "security_question",    "TEXT"),
        ("users", "security_answer_hash", "TEXT"),
        ("users", "recovery_code",        "TEXT UNIQUE"),
        ("users", "full_name",            "TEXT"),
        ("users", "country_code",         "TEXT DEFAULT '+256'"),
        ("users", "gender",               "TEXT"),
        ("users", "dob",                  "TEXT"),
        ("users", "bio",                  "TEXT"),
        ("users", "profile_pic",          "TEXT"),
        ("users", "theme",                "TEXT NOT NULL DEFAULT 'dark'"),
        ("users", "status",               "TEXT NOT NULL DEFAULT 'active'"),
        ("users", "totp_secret",          "TEXT"),
        ("logs",  "user_id",              "INTEGER"),
        ("logs",  "username",             "TEXT"),
        ("logs",  "ip_address",           "TEXT"),
        ("logs",  "details",              "TEXT"),
    ]
    for table, col, col_type in migrations:
        try:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
        except sqlite3.OperationalError:
            pass  # Column already exists