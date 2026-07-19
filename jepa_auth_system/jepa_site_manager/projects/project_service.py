"""Project management service for JEPA Site Manager."""

from jepa_site_manager.database.connection import get_connection
from jepa_site_manager.core.activity_service import log_activity
from .models import ProjectRecord


def create_project(record: ProjectRecord | None = None, user_id: int | None = None, **kwargs) -> int:
    """Create a project record linked to the existing user system.

    This accepts either the existing ProjectRecord model or keyword arguments,
    which keeps the interface flexible for the new project-centric workflow.
    """
    if record is None:
        record = ProjectRecord(**kwargs)
    elif isinstance(record, dict):
        record = ProjectRecord(**record)

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO projects (
                project_name, client, location, budget, start_date, end_date, status, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.project_name,
                record.client,
                record.location,
                record.budget,
                record.start_date,
                record.end_date,
                record.status,
                record.created_by or user_id,
            ),
        )
        conn.commit()
        project_id = int(cursor.lastrowid)
    
    # Log activity
    if user_id:
        log_activity(
            project_id=project_id,
            user_id=user_id,
            action_type="CREATE",
            subject="Project",
            detail=f"Created project '{record.project_name}'"
        )
    
    return project_id


def get_project(project_id: int) -> dict | None:
    """Retrieve a single project by ID."""
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, project_name, client, location, budget, start_date, end_date, status, created_at, created_by
            FROM projects
            WHERE id = ?
            """,
            (project_id,)
        ).fetchone()
    return dict(row) if row else None


def list_projects(status_filter: str | None = None) -> list[dict]:
    """Return all project rows in order of latest creation. Optionally filter by status."""
    query = """
        SELECT id, project_name, client, location, budget, start_date, end_date, status, created_at
        FROM projects
    """
    params = []
    
    if status_filter:
        query += " WHERE status = ?"
        params.append(status_filter)
    
    query += " ORDER BY id DESC"
    
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def update_project(project_id: int, updates: dict, user_id: int | None = None) -> bool:
    """Update project fields. Returns True if successful."""
    if not updates:
        return False
    
    # Whitelist allowed fields
    allowed_fields = {"project_name", "client", "location", "budget", "start_date", "end_date", "status"}
    updates = {k: v for k, v in updates.items() if k in allowed_fields}
    
    if not updates:
        return False
    
    set_clause = ", ".join(f"{field} = ?" for field in updates.keys())
    values = list(updates.values()) + [project_id]
    
    with get_connection() as conn:
        cursor = conn.execute(
            f"UPDATE projects SET {set_clause} WHERE id = ?",
            values
        )
        conn.commit()
    
    # Log activity
    if user_id:
        log_activity(
            project_id=project_id,
            user_id=user_id,
            action_type="UPDATE",
            subject="Project",
            detail=f"Updated fields: {', '.join(updates.keys())}"
        )
    
    return cursor.rowcount > 0


def delete_project(project_id: int, user_id: int | None = None) -> bool:
    """Delete a project. Returns True if successful."""
    # First get project name for logging
    project = get_project(project_id)
    if not project:
        return False
    
    with get_connection() as conn:
        # Check for linked records
        task_count = conn.execute("SELECT COUNT(*) as cnt FROM tasks WHERE project_id = ?", (project_id,)).fetchone()["cnt"]
        site_count = conn.execute("SELECT COUNT(*) as cnt FROM sites WHERE project_id = ?", (project_id,)).fetchone()["cnt"]
        material_count = conn.execute("SELECT COUNT(*) as cnt FROM materials WHERE project_id = ?", (project_id,)).fetchone()["cnt"]
        
        if task_count > 0 or site_count > 0 or material_count > 0:
            # Don't delete if there are related records - just mark as archived
            cursor = conn.execute(
                "UPDATE projects SET status = 'Archived' WHERE id = ?",
                (project_id,)
            )
            conn.commit()
            
            if user_id:
                log_activity(
                    project_id=project_id,
                    user_id=user_id,
                    action_type="UPDATE",
                    subject="Project",
                    detail=f"Archived project (had {task_count} tasks, {site_count} sites, {material_count} materials)"
                )
            return True
        else:
            # Safe to delete
            cursor = conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            conn.commit()
            
            if user_id:
                log_activity(
                    project_id=project_id,
                    user_id=user_id,
                    action_type="DELETE",
                    subject="Project",
                    detail=f"Deleted project '{project['project_name']}'"
                )
            return cursor.rowcount > 0


def get_project_stats(project_id: int) -> dict:
    """Get summary statistics for a project."""
    with get_connection() as conn:
        project = conn.execute(
            "SELECT * FROM projects WHERE id = ?",
            (project_id,)
        ).fetchone()
        
        if not project:
            return {}
        
        task_count = conn.execute(
            "SELECT COUNT(*) as cnt FROM tasks WHERE project_id = ?",
            (project_id,)
        ).fetchone()["cnt"]
        
        completed_tasks = conn.execute(
            "SELECT COUNT(*) as cnt FROM tasks WHERE project_id = ? AND status = 'Completed'",
            (project_id,)
        ).fetchone()["cnt"]
        
        site_count = conn.execute(
            "SELECT COUNT(*) as cnt FROM sites WHERE project_id = ?",
            (project_id,)
        ).fetchone()["cnt"]
        
        material_count = conn.execute(
            "SELECT COUNT(*) as cnt FROM materials WHERE project_id = ?",
            (project_id,)
        ).fetchone()["cnt"]
        
        low_stock = conn.execute(
            """SELECT COUNT(*) as cnt FROM materials 
               WHERE project_id = ? AND (balance / quantity * 100) < 20""",
            (project_id,)
        ).fetchone()["cnt"]
        
        issue_count = conn.execute(
            "SELECT COUNT(*) as cnt FROM issues WHERE project_id = ? AND status != 'Closed'",
            (project_id,)
        ).fetchone()["cnt"]
    
    return {
        "project": dict(project),
        "tasks": {"total": task_count, "completed": completed_tasks},
        "sites": site_count,
        "materials": {"total": material_count, "low_stock": low_stock},
        "open_issues": issue_count,
    }
