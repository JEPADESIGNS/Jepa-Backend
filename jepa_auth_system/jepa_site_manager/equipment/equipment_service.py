"""Equipment management service for JEPA Site Manager."""

from datetime import datetime

from jepa_site_manager.database.connection import get_connection
from jepa_site_manager.core.activity_service import log_activity


def create_equipment(
    project_id: int,
    equipment_name: str,
    equipment_type: str = "",
    status: str = "Available",
    location: str | None = None,
    maintenance_date: str | None = None,
    assigned_site_id: int | None = None,
    created_by: int | None = None,
    notes: str | None = None,
) -> dict:
    if not project_id:
        raise ValueError("project_id is required")
    if not equipment_name or not equipment_name.strip():
        raise ValueError("equipment_name is required")

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO equipment (
                project_id,
                equipment_name,
                equipment_type,
                status,
                location,
                maintenance_date,
                assigned_site_id,
                created_by,
                notes,
                created_at,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                equipment_name.strip(),
                equipment_type.strip(),
                status,
                location,
                maintenance_date,
                assigned_site_id,
                created_by,
                notes,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
            ),
        )
        conn.commit()
        equipment_id = int(cursor.lastrowid)

    log_activity(
        project_id=project_id,
        user_id=created_by,
        action_type="equipment_created",
        subject=equipment_name.strip(),
        detail=f"status={status}; assigned_site_id={assigned_site_id}",
    )

    return get_equipment(equipment_id)


def get_equipment(equipment_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM equipment WHERE id = ?",
            (equipment_id,),
        ).fetchone()
    return dict(row) if row else None


def list_equipment(project_id: int) -> list[dict]:
    if not project_id:
        raise ValueError("project_id is required")

    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM equipment WHERE project_id = ? ORDER BY created_at DESC",
            (project_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def update_status(equipment_id: int, status: str, updated_by: int | None = None) -> dict:
    if not equipment_id:
        raise ValueError("equipment_id is required")
    if not status or not status.strip():
        raise ValueError("status is required")

    with get_connection() as conn:
        conn.execute(
            "UPDATE equipment SET status = ?, updated_at = ? WHERE id = ?",
            (status.strip(), datetime.now().isoformat(), equipment_id),
        )
        conn.commit()
        equipment = get_equipment(equipment_id)

    if equipment:
        log_activity(
            project_id=equipment["project_id"],
            user_id=updated_by,
            action_type="equipment_status_updated",
            subject=equipment["equipment_name"],
            detail=f"status={status.strip()}",
        )

    return equipment


def maintenance_log(equipment_id: int) -> dict | None:
    return get_equipment(equipment_id)
