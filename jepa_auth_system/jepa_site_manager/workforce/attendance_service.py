"""Attendance management service for JEPA Site Manager.

BIOMETRIC INTEGRATION REQUIREMENTS:
- All attendance records MUST be authenticated via biometric (fingerprint/face recognition)
- Physical ID card scanning is REQUIRED for every team member entry
- Biometric data is stored separately for security and audit compliance
"""

from datetime import datetime, timedelta

from jepa_site_manager.database.connection import get_connection
from jepa_site_manager.core.activity_service import log_activity


def mark_attendance(
    project_id: int,
    user_id: int,
    attendance_date: str,
    status: str = "Present",
    site_id: int | None = None,
    time_in: str | None = None,
    time_out: str | None = None,
    notes: str | None = None,
    biometric_type: str | None = None,  # "fingerprint" or "face_recognition"
    biometric_data: str | None = None,  # hash/token from biometric scanner
    physical_id: str | None = None,  # Physical ID card number
    verified_by_biometric: bool = False,
    verified_by_physical_id: bool = False,
) -> dict:
    """Mark attendance with REQUIRED biometric + physical ID verification.
    
    MANDATORY REQUIREMENTS:
    - Biometric verification (fingerprint or face recognition) MUST be successful
    - Physical ID card scan MUST be verified
    - Both verification methods must be confirmed before record is saved
    
    Args:
        biometric_type: "fingerprint" or "face_recognition"
        biometric_data: Token/hash from biometric device confirming match
        physical_id: Physical ID card number/UUID scanned
        verified_by_biometric: Boolean flag from biometric device
        verified_by_physical_id: Boolean flag from ID scanner device
    """
    if not project_id:
        raise ValueError("project_id is required")
    if not user_id:
        raise ValueError("user_id is required")
    if not attendance_date:
        raise ValueError("attendance_date is required")
    
    # MANDATORY: Biometric verification
    if not verified_by_biometric or not biometric_type:
        raise ValueError("❌ Biometric verification REQUIRED: Fingerprint or Face Recognition scan failed")
    
    # MANDATORY: Physical ID verification
    if not verified_by_physical_id or not physical_id:
        raise ValueError("❌ Physical ID card scan REQUIRED: ID could not be verified")
    
    if biometric_type not in ["fingerprint", "face_recognition"]:
        raise ValueError("Biometric type must be 'fingerprint' or 'face_recognition'")

    with get_connection() as conn:
        # Check if record exists for this user/project/date
        existing = conn.execute(
            "SELECT id FROM attendance WHERE project_id = ? AND user_id = ? AND attendance_date = ?",
            (project_id, user_id, attendance_date)
        ).fetchone()
        
        if existing:
            # Update existing record with new biometric/ID verification
            cursor = conn.execute(
                """
                UPDATE attendance SET 
                    site_id = ?, time_in = ?, time_out = ?, status = ?, notes = ?,
                    biometric_type = ?, biometric_data = ?, physical_id = ?, verified_at = ?
                WHERE id = ?
                """,
                (
                    site_id, time_in, time_out, status, notes,
                    biometric_type, biometric_data, physical_id, datetime.now().isoformat(),
                    existing["id"]
                )
            )
            conn.commit()
            record_id = existing["id"]
        else:
            # Insert new record with biometric + physical ID verification
            cursor = conn.execute(
                """
                INSERT INTO attendance (
                    project_id,
                    site_id,
                    user_id,
                    attendance_date,
                    time_in,
                    time_out,
                    status,
                    notes,
                    biometric_type,
                    biometric_data,
                    physical_id,
                    verified_at,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    site_id,
                    user_id,
                    attendance_date,
                    time_in,
                    time_out,
                    status,
                    notes,
                    biometric_type,
                    biometric_data,
                    physical_id,
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()
            record_id = int(cursor.lastrowid)

    log_activity(
        project_id=project_id,
        user_id=user_id,
        action_type="attendance_marked_biometric",
        subject=f"Attendance {attendance_date}",
        detail=f"biometric={biometric_type}; physical_id={physical_id}; status={status}; site_id={site_id}",
    )

    return get_attendance_by_id(record_id)


def log_biometric_verification(
    attendance_id: int,
    user_id: int,
    project_id: int,
    biometric_type: str,
    physical_id: str,
    biometric_data: str,
    verification_status: str = "Success",
    device_id: str | None = None,
) -> dict:
    """Log biometric verification attempt for audit compliance.
    
    Creates an immutable audit trail of all biometric verification events.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO biometric_verification (
                attendance_id,
                user_id,
                project_id,
                biometric_type,
                physical_id,
                biometric_data,
                verification_status,
                device_id,
                verified_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                attendance_id,
                user_id,
                project_id,
                biometric_type,
                physical_id,
                biometric_data,
                verification_status,
                device_id,
                datetime.now().isoformat(),
            ),
        )
        conn.commit()
        record_id = int(cursor.lastrowid)
    
    return get_biometric_verification_by_id(record_id)


def log_physical_id_scan(
    user_id: int,
    project_id: int,
    physical_id: str,
    scan_status: str = "Valid",
    device_id: str | None = None,
    id_type: str = "Employee Card",
    notes: str | None = None,
) -> dict:
    """Log physical ID card scan for audit compliance.
    
    Creates an immutable audit trail of all ID card scan events.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO physical_id_scan (
                user_id,
                project_id,
                physical_id,
                id_type,
                scanner_device_id,
                scan_status,
                notes,
                scan_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                project_id,
                physical_id,
                id_type,
                device_id,
                scan_status,
                notes,
                datetime.now().isoformat(),
            ),
        )
        conn.commit()
        record_id = int(cursor.lastrowid)
    
    return get_physical_id_scan_by_id(record_id)


def get_biometric_verification_by_id(record_id: int) -> dict | None:
    """Retrieve a biometric verification record."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM biometric_verification WHERE id = ?",
            (record_id,),
        ).fetchone()
    return dict(row) if row else None


def get_physical_id_scan_by_id(record_id: int) -> dict | None:
    """Retrieve a physical ID scan record."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM physical_id_scan WHERE id = ?",
            (record_id,),
        ).fetchone()
    return dict(row) if row else None


def get_biometric_verification_history(user_id: int, project_id: int, limit: int = 50) -> list[dict]:
    """Get biometric verification audit trail for a user."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM biometric_verification 
            WHERE user_id = ? AND project_id = ? 
            ORDER BY verified_at DESC LIMIT ?
            """,
            (user_id, project_id, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def get_physical_id_scan_history(user_id: int, project_id: int, limit: int = 50) -> list[dict]:
    """Get physical ID scan audit trail for a user."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM physical_id_scan 
            WHERE user_id = ? AND project_id = ? 
            ORDER BY scan_timestamp DESC LIMIT ?
            """,
            (user_id, project_id, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def get_attendance_by_id(record_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM attendance WHERE id = ?",
            (record_id,),
        ).fetchone()
    return dict(row) if row else None


def get_attendance_by_project(project_id: int) -> list[dict]:
    if not project_id:
        raise ValueError("project_id is required")

    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM attendance WHERE project_id = ? ORDER BY attendance_date DESC, id DESC",
            (project_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_attendance_by_date(attendance_date: str, project_id: int | None = None) -> list[dict]:
    """Retrieve attendance rows for a given date.

    If `project_id` is provided, filter to that project. This signature is
    backward-compatible with callers that pass (date, project_id).
    """
    if not attendance_date:
        raise ValueError("attendance_date is required")

    with get_connection() as conn:
        if project_id:
            rows = conn.execute(
                "SELECT * FROM attendance WHERE attendance_date = ? AND project_id = ? ORDER BY user_id",
                (attendance_date, project_id),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM attendance WHERE attendance_date = ? ORDER BY project_id, user_id",
                (attendance_date,),
            ).fetchall()
    return [dict(row) for row in rows]


def get_attendance_stats(project_id: int, attendance_date: str | None = None) -> dict:
    """Get attendance statistics for a project on a specific date."""
    today = datetime.now().strftime("%Y-%m-%d")
    query_date = attendance_date or today
    
    with get_connection() as conn:
        present = conn.execute(
            "SELECT COUNT(*) as cnt FROM attendance WHERE project_id = ? AND attendance_date = ? AND status = 'Present'",
            (project_id, query_date)
        ).fetchone()["cnt"]
        
        absent = conn.execute(
            "SELECT COUNT(*) as cnt FROM attendance WHERE project_id = ? AND attendance_date = ? AND status = 'Absent'",
            (project_id, query_date)
        ).fetchone()["cnt"]
        
        late = conn.execute(
            "SELECT COUNT(*) as cnt FROM attendance WHERE project_id = ? AND attendance_date = ? AND status = 'Late'",
            (project_id, query_date)
        ).fetchone()["cnt"]
        
        on_leave = conn.execute(
            "SELECT COUNT(*) as cnt FROM attendance WHERE project_id = ? AND attendance_date = ? AND status = 'On Leave'",
            (project_id, query_date)
        ).fetchone()["cnt"]
        
        total = present + absent + late + on_leave
    
    return {
        "date": query_date,
        "present": present,
        "absent": absent,
        "late": late,
        "on_leave": on_leave,
        "total": total,
    }


def get_project_attendance_summary(project_id: int, days: int = 30) -> dict:
    """Get attendance summary for a project over N days."""
    today = datetime.now()
    start_date = (today - timedelta(days=days)).strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")
    
    with get_connection() as conn:
        total_records = conn.execute(
            "SELECT COUNT(*) as cnt FROM attendance WHERE project_id = ? AND attendance_date BETWEEN ? AND ?",
            (project_id, start_date, end_date)
        ).fetchone()["cnt"]
        
        present_count = conn.execute(
            """SELECT COUNT(*) as cnt FROM attendance 
               WHERE project_id = ? AND attendance_date BETWEEN ? AND ? AND status = 'Present'""",
            (project_id, start_date, end_date)
        ).fetchone()["cnt"]
        
        present_percentage = int((present_count / total_records * 100)) if total_records > 0 else 0
    
    return {
        "period_days": days,
        "total_records": total_records,
        "present_percentage": present_percentage,
    }
