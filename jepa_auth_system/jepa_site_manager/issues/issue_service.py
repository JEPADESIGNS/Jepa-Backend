"""Issue management service for JEPA Site Manager."""

from datetime import datetime

from jepa_site_manager.database.connection import get_connection
from jepa_site_manager.core.activity_service import log_activity


def create_issue(
    project_id: int,
    title: str,
    description: str = "",
    priority: str = "Medium",
    created_by: int | None = None,
    assigned_to_id: int | None = None,
    status: str = "Open",
    resolution_notes: str | None = None,
) -> dict:
    if not project_id:
        raise ValueError("project_id is required")
    if not title or not title.strip():
        raise ValueError("title is required")

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO issues (
                project_id,
                title,
                description,
                priority,
                status,
                raised_by_id,
                assigned_to_id,
                resolution_notes,
                created_at,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                title.strip(),
                description.strip(),
                priority,
                status,
                created_by,
                assigned_to_id,
                resolution_notes,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
            ),
        )
        conn.commit()
        issue_id = int(cursor.lastrowid)

    log_activity(
        project_id=project_id,
        user_id=created_by,
        action_type="issue_created",
        subject=title.strip(),
        detail=f"Priority={priority}; status={status}",
    )

    return get_issue(issue_id)


def get_issue(issue_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM issues WHERE id = ?",
            (issue_id,),
        ).fetchone()
    return dict(row) if row else None


def list_issues(project_id: int) -> list[dict]:
    if not project_id:
        raise ValueError("project_id is required")

    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM issues WHERE project_id = ? ORDER BY created_at DESC",
            (project_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def update_issue(issue_id: int, **fields) -> dict:
    if not issue_id:
        raise ValueError("issue_id is required")
    allowed = {
        "title",
        "description",
        "priority",
        "status",
        "assigned_to_id",
        "resolution_notes",
    }
    updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if not updates:
        raise ValueError("No valid fields provided for update")

    updates["updated_at"] = datetime.now().isoformat()
    set_clause = ", ".join(f"{key} = ?" for key in updates)
    params = list(updates.values()) + [issue_id]

    with get_connection() as conn:
        conn.execute(
            f"UPDATE issues SET {set_clause} WHERE id = ?",
            params,
        )
        conn.commit()

        issue = get_issue(issue_id)

    if issue:
        log_activity(
            project_id=issue["project_id"],
            user_id=fields.get("updated_by"),
            action_type="issue_updated",
            subject=issue["title"],
            detail=", ".join(f"{k}={v}" for k, v in updates.items() if k != "updated_at"),
        )

    return issue


def assign_issue(issue_id: int, assigned_to_id: int, assigned_by: int | None = None) -> dict:
    if not issue_id:
        raise ValueError("issue_id is required")
    if not assigned_to_id:
        raise ValueError("assigned_to_id is required")

    with get_connection() as conn:
        conn.execute(
            "UPDATE issues SET assigned_to_id = ?, updated_at = ? WHERE id = ?",
            (assigned_to_id, datetime.now().isoformat(), issue_id),
        )
        conn.commit()
        issue = get_issue(issue_id)

    if issue:
        log_activity(
            project_id=issue["project_id"],
            user_id=assigned_by,
            action_type="issue_assigned",
            subject=issue["title"],
            detail=f"assigned_to_id={assigned_to_id}",
        )

    return issue


def resolve_issue(issue_id: int, resolution_notes: str, resolved_by: int | None = None) -> dict:
    if not issue_id:
        raise ValueError("issue_id is required")
    if resolution_notes is None:
        raise ValueError("resolution_notes is required")

    with get_connection() as conn:
        conn.execute(
            "UPDATE issues SET status = ?, resolution_notes = ?, updated_at = ? WHERE id = ?",
            ("Resolved", resolution_notes.strip(), datetime.now().isoformat(), issue_id),
        )
        conn.commit()
        issue = get_issue(issue_id)

    if issue:
        log_activity(
            project_id=issue["project_id"],
            user_id=resolved_by,
            action_type="issue_resolved",
            subject=issue["title"],
            detail=f"resolution_notes={resolution_notes.strip()}",
        )

    return issue


def delete_issue(issue_id: int, deleted_by: int | None = None) -> None:
    """Delete an issue by id."""
    if not issue_id:
        raise ValueError("issue_id is required")

    with get_connection() as conn:
        # Keep a copy for logging
        row = conn.execute("SELECT project_id, title FROM issues WHERE id = ?", (issue_id,)).fetchone()
        conn.execute("DELETE FROM issues WHERE id = ?", (issue_id,))
        conn.commit()

    if row:
        log_activity(
            project_id=row["project_id"],
            user_id=deleted_by,
            action_type="issue_deleted",
            subject=row["title"],
            detail=f"deleted id={issue_id}",
        )
