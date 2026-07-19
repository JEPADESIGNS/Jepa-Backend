"""Material tracking service for JEPA Site Manager."""

from jepa_site_manager.database.connection import get_connection


def create_material(project_id: int, material_name: str, quantity: float = 0, supplier: str = "", date_received: str | None = None, date_issued: str | None = None, balance: float | None = None, created_by: int | None = None) -> int:
    """Create a material record linked to a project."""
    if balance is None:
        balance = quantity

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO materials (project_id, material_name, quantity, supplier, date_received, date_issued, balance, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (project_id, material_name, quantity, supplier, date_received, date_issued, balance, created_by),
        )
        conn.commit()
        return int(cursor.lastrowid)


def list_materials(project_id: int | None = None) -> list[dict]:
    """List material records, optionally filtered by project."""
    with get_connection() as conn:
        if project_id is None:
            rows = conn.execute("SELECT * FROM materials ORDER BY id DESC").fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM materials WHERE project_id = ? ORDER BY id DESC",
                (project_id,),
            ).fetchall()
    return [dict(row) for row in rows]
