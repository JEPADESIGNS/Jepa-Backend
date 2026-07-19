"""Dashboard analytics and metrics service for the command center."""

from datetime import datetime, timedelta
from jepa_site_manager.database.connection import get_connection


def get_active_projects_count() -> int:
    """Return count of active projects (not Completed or On Hold)."""
    with get_connection() as conn:
        result = conn.execute(
            "SELECT COUNT(*) as count FROM projects WHERE status NOT IN ('Completed', 'On Hold')"
        ).fetchone()
    return result["count"] if result else 0


def get_delayed_projects_count() -> int:
    """Return count of projects with delayed tasks or no recent reports."""
    with get_connection() as conn:
        delayed = conn.execute(
            """
            SELECT COUNT(DISTINCT p.id) as count
            FROM projects p
            LEFT JOIN tasks t ON p.id = t.project_id
            WHERE (t.status IN ('Planned', 'In Progress') AND t.progress_percent < 50)
            OR (p.end_date IS NOT NULL AND p.end_date < DATE('now') AND p.status != 'Completed')
            """
        ).fetchone()
    return delayed["count"] if delayed else 0


def get_missing_reports_count() -> int:
    """Return count of projects with no report for today."""
    today = datetime.now().strftime("%Y-%m-%d")
    with get_connection() as conn:
        active_projects = conn.execute(
            "SELECT id FROM projects WHERE status NOT IN ('Completed', 'On Hold')"
        ).fetchall()
        
        projects_with_reports_today = conn.execute(
            f"SELECT DISTINCT project_id FROM site_reports WHERE report_date = '{today}'"
        ).fetchall()
    
    reported_ids = {row["project_id"] for row in projects_with_reports_today}
    active_ids = {row["id"] for row in active_projects}
    return len(active_ids - reported_ids)


def get_low_stock_alerts() -> list[dict]:
    """Return materials with balance below 20% of original quantity."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT m.id, m.material_name, m.quantity, m.balance, p.project_name
            FROM materials m
            JOIN projects p ON m.project_id = p.id
            WHERE m.balance < (m.quantity * 0.2) AND m.balance > 0
            ORDER BY m.balance ASC
            LIMIT 5
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_workforce_on_site_count() -> int:
    """Estimated workforce count from latest site reports."""
    with get_connection() as conn:
        latest_reports = conn.execute(
            """
            SELECT workers_present FROM site_reports
            WHERE report_date = DATE('now')
            ORDER BY created_at DESC LIMIT 5
            """
        ).fetchall()
    
    total_count = 0
    for row in latest_reports:
        try:
            if row["workers_present"]:
                total_count += int(row["workers_present"].split()[0])
        except (ValueError, IndexError):
            pass
    return total_count


def get_project_summary() -> list[dict]:
    """Return project summary with name, progress, status, and last report date."""
    with get_connection() as conn:
        projects = conn.execute(
            """
            SELECT 
                p.id,
                p.project_name,
                p.status,
                p.start_date,
                p.end_date,
                COALESCE(AVG(t.progress_percent), 0) as progress_percent,
                (SELECT MAX(report_date) FROM site_reports WHERE project_id = p.id) as last_report_date
            FROM projects p
            LEFT JOIN tasks t ON p.id = t.project_id
            WHERE p.status NOT IN ('Completed', 'On Hold')
            GROUP BY p.id
            ORDER BY p.created_at DESC
            LIMIT 8
            """
        ).fetchall()
    return [dict(row) for row in projects]


def get_recent_activity(limit: int = 12) -> list[dict]:
    """Return recent activity timeline from projects, reports, tasks, and materials."""
    with get_connection() as conn:
        reports = conn.execute(
            """
            SELECT 
                'Report' as type,
                sr.created_at as timestamp,
                p.project_name as subject,
                'Daily site report submitted' as action,
                NULL as detail
            FROM site_reports sr
            JOIN projects p ON sr.project_id = p.id
            ORDER BY sr.created_at DESC
            LIMIT 4
            """
        ).fetchall()
        
        tasks_updated = conn.execute(
            """
            SELECT 
                'Task' as type,
                t.updated_at as timestamp,
                p.project_name as subject,
                t.title as action,
                t.status as detail
            FROM tasks t
            JOIN projects p ON t.project_id = p.id
            WHERE t.updated_at IS NOT NULL
            ORDER BY t.updated_at DESC
            LIMIT 4
            """
        ).fetchall()
        
        materials_added = conn.execute(
            """
            SELECT 
                'Material' as type,
                m.created_at as timestamp,
                p.project_name as subject,
                m.material_name as action,
                CAST(m.quantity AS TEXT) || ' units received' as detail
            FROM materials m
            JOIN projects p ON m.project_id = p.id
            ORDER BY m.created_at DESC
            LIMIT 4
            """
        ).fetchall()
    
    # Combine and sort by timestamp
    all_activity = []
    for row in reports:
        all_activity.append(dict(row))
    for row in tasks_updated:
        all_activity.append(dict(row))
    for row in materials_added:
        all_activity.append(dict(row))
    
    all_activity.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return all_activity[:limit]


def get_equipment_issues_count() -> int:
    """Placeholder for equipment issues (not yet implemented in schema)."""
    return 0


def get_admin_dashboard_metrics() -> dict:
    """Return all key metrics for the admin dashboard."""
    return {
        "active_projects": get_active_projects_count(),
        "delayed_projects": get_delayed_projects_count(),
        "missing_reports": get_missing_reports_count(),
        "low_stock_alerts": get_low_stock_alerts(),
        "workforce_on_site": get_workforce_on_site_count(),
        "equipment_issues": get_equipment_issues_count(),
        "project_summary": get_project_summary(),
        "recent_activity": get_recent_activity(),
    }
