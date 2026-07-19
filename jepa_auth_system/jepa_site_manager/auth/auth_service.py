"""Authentication service built on top of the existing login logic."""

from database.db import get_connection
from auth.security import verify_password


def authenticate(identity: str, password: str) -> dict | None:
    """Validate a username/email/phone login and return the user row."""
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, username, email, password_hash, role, status, theme, totp_secret
            FROM users
            WHERE username = ? OR email = ? OR phone = ?
            """,
            (identity, identity, identity),
        ).fetchone()

    if not row:
        return None

    if row["status"] == "suspended":
        return None

    if not verify_password(password, row["password_hash"]):
        return None

    return dict(row)
