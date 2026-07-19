"""Basic task management service for JEPA Site Manager."""

from jepa_site_manager.database.connection import get_connection


def create_task(project_id: int, site_id: int | None = None, title: str = "", status: str = "Planned", progress_percent: int = 0, assigned_user_id: int | None = None) -> int:
    """Create a simple task linked to a project and optional site."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO tasks (project_id, site_id, title, status, progress_percent, assigned_user_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (project_id, site_id, title, status, progress_percent, assigned_user_id),
        )
        conn.commit()
        return int(cursor.lastrowid)


def list_tasks(project_id: int | None = None) -> list[dict]:
    """List tasks, optionally filtered by project."""
    with get_connection() as conn:
        if project_id is None:
            rows = conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE project_id = ? ORDER BY id DESC",
                (project_id,),
            ).fetchall()
    return [dict(row) for row in rows]
