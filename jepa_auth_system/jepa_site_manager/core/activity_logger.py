"""Activity logging adapter for the modular JEPA Site Manager package."""

from utils.logger import log_activity


def record(action: str, user_id: int | None = None, username: str | None = None, details: str | None = None) -> None:
    """Record an activity entry using the existing logger."""
    log_activity(action, user_id=user_id, username=username, details=details)
