"""Activity logging service for JEPA Site Manager."""

from datetime import datetime

from jepa_site_manager.database.connection import get_connection


def log_activity(
    project_id: int,
    user_id: int | None,
    action_type: str,
    subject: str | None = None,
    detail: str | None = None,
    timestamp: str | None = None,
) -> dict:
    if not project_id:
        raise ValueError("project_id is required")
    if not action_type or not action_type.strip():
        raise ValueError("action_type is required")

    actual_timestamp = timestamp or datetime.now().isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO activity_log (
                project_id,
                user_id,
                action_type,
                subject,
                detail,
                timestamp
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                user_id,
                action_type.strip(),
                subject,
                detail,
                actual_timestamp,
            ),
        )
        conn.commit()
        activity_id = int(cursor.lastrowid)

    return get_activity(activity_id)


def get_activity(activity_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM activity_log WHERE id = ?",
            (activity_id,),
        ).fetchone()
    return dict(row) if row else None


def get_project_activity(project_id: int, limit: int = 25) -> list[dict]:
    if not project_id:
        raise ValueError("project_id is required")

    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM activity_log WHERE project_id = ? ORDER BY timestamp DESC LIMIT ?",
            (project_id, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def get_user_activity(user_id: int, limit: int = 25) -> list[dict]:
    if not user_id:
        raise ValueError("user_id is required")

    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM activity_log WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    return [dict(row) for row in rows]
