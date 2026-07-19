"""
utils/logger.py — Structured activity logging to the logs table.
"""
from database.db import get_connection


def log_activity(
    action: str,
    user_id: int | None = None,
    username: str | None = None,
    details: str | None = None,
    ip_address: str | None = None,
):
    """Insert a row into the logs table. Silently swallows errors to avoid
    disrupting the main application flow."""
    try:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO logs (user_id, username, action, ip_address, details)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, username, action, ip_address, details),
            )
            conn.commit()
    except Exception:
        pass
