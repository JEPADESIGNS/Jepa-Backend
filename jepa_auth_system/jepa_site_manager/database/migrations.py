"""Migration helpers for the JEPA Site Manager database extensions."""

from .connection import ensure_schema


def apply_migrations() -> None:
    """Apply the modular schema extensions to the existing SQLite database."""
    ensure_schema()
