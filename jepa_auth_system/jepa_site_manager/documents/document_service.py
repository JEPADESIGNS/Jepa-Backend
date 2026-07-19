"""Document metadata service for JEPA Site Manager."""

from datetime import datetime

from jepa_site_manager.database.connection import get_connection
from jepa_site_manager.core.activity_service import log_activity


def upload_document(
    project_id: int,
    title: str,
    document_type: str | None = None,
    file_path: str | None = None,
    uploaded_by: int | None = None,
    description: str | None = None,
) -> dict:
    if not project_id:
        raise ValueError("project_id is required")
    if not title or not title.strip():
        raise ValueError("title is required")

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO documents (
                project_id,
                title,
                document_type,
                file_path,
                uploaded_by,
                uploaded_at,
                description
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                title.strip(),
                document_type,
                file_path,
                uploaded_by,
                datetime.now().isoformat(),
                description,
            ),
        )
        conn.commit()
        document_id = int(cursor.lastrowid)

    log_activity(
        project_id=project_id,
        user_id=uploaded_by,
        action_type="document_uploaded",
        subject=title.strip(),
        detail=f"type={document_type}",
    )

    return get_document(document_id)


def get_document(document_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM documents WHERE id = ?",
            (document_id,),
        ).fetchone()
    return dict(row) if row else None


def list_documents(project_id: int) -> list[dict]:
    if not project_id:
        raise ValueError("project_id is required")

    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM documents WHERE project_id = ? ORDER BY uploaded_at DESC",
            (project_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def delete_document(document_id: int, deleted_by: int | None = None) -> bool:
    document = get_document(document_id)
    if not document:
        return False

    with get_connection() as conn:
        conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))
        conn.commit()

    log_activity(
        project_id=document["project_id"],
        user_id=deleted_by,
        action_type="document_deleted",
        subject=document["title"],
        detail=f"document_id={document_id}",
    )

    return True


def update_document(document_id: int, title: str | None = None, document_type: str | None = None, description: str | None = None, updated_by: int | None = None) -> dict | None:
    """Update document metadata."""
    if not document_id:
        raise ValueError("document_id is required")

    doc = get_document(document_id)
    if not doc:
        return None

    fields = []
    params = []
    if title is not None:
        fields.append("title = ?"); params.append(title.strip())
    if document_type is not None:
        fields.append("document_type = ?"); params.append(document_type)
    if description is not None:
        fields.append("description = ?"); params.append(description)
    if not fields:
        return get_document(document_id)

    params.append(document_id)
    sql = f"UPDATE documents SET {', '.join(fields)}, uploaded_at = ? WHERE id = ?"
    params.insert(-1, datetime.now().isoformat())

    with get_connection() as conn:
        conn.execute(sql, tuple(params))
        conn.commit()

    log_activity(
        project_id=doc["project_id"],
        user_id=updated_by,
        action_type="document_updated",
        subject=title or doc["title"],
        detail=f'document_id={document_id}',
    )

    return get_document(document_id)
