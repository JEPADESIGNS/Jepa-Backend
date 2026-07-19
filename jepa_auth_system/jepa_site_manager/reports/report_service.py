"""Daily site report helpers for JEPA Site Manager."""

from jepa_site_manager.database.connection import get_connection


def create_report(project_id: int, report_date: str, weather: str = "", activities: str = "", workers_present: str = "", issues: str = "", photo_path: str | None = None, created_by: int | None = None) -> int:
    """Create a daily site report for a project."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO site_reports (project_id, report_date, weather, activities, workers_present, issues, photo_path, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (project_id, report_date, weather, activities, workers_present, issues, photo_path, created_by),
        )
        conn.commit()
        return int(cursor.lastrowid)


def list_reports(project_id: int | None = None) -> list[dict]:
    """List site reports, optionally filtered by project."""
    with get_connection() as conn:
        if project_id is None:
            rows = conn.execute("SELECT * FROM site_reports ORDER BY id DESC").fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM site_reports WHERE project_id = ? ORDER BY id DESC",
                (project_id,),
            ).fetchall()
    return [dict(row) for row in rows]
