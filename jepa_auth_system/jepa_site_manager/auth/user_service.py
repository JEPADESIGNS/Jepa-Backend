"""User-management helpers for the modular JEPA Site Manager layer."""

from database.db import get_connection


def list_users() -> list[dict]:
    """Return the current user roster, preserving existing authentication data."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, username, email, role, status, theme, created_at
            FROM users
            ORDER BY id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]
