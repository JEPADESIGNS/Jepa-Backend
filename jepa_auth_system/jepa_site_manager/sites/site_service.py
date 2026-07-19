"""Basic site management service for JEPA Site Manager."""

from jepa_site_manager.database.connection import get_connection


def create_site(project_id: int, site_name: str, location: str = "", site_type: str = "Main Site", status: str = "Active", responsible_user_id: int | None = None) -> int:
    """Create a site linked to a project."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO sites (project_id, site_name, location, site_type, status, responsible_user_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (project_id, site_name, location, site_type, status, responsible_user_id),
        )
        conn.commit()
        return int(cursor.lastrowid)


def list_sites(project_id: int | None = None) -> list[dict]:
    """List sites, optionally filtered by project."""
    with get_connection() as conn:
        if project_id is None:
            rows = conn.execute("SELECT * FROM sites ORDER BY id DESC").fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM sites WHERE project_id = ? ORDER BY id DESC",
                (project_id,),
            ).fetchall()
    return [dict(row) for row in rows]
