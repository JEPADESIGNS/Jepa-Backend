"""Operations intelligence service for the Morning Operations Center.

Provides role-specific insights, priorities, alerts, and activities.
"""

from datetime import datetime, timedelta
from jepa_site_manager.database.connection import get_connection


def get_today_priorities(user_id: int, role: str) -> list[dict]:
    """Get prioritized action items for the user based on role."""
    priorities = []
    today = datetime.now().strftime("%Y-%m-%d")
    
    with get_connection() as conn:
        # Reports missing for today (all roles except client)
        if role not in ("client",):
            missing_reports = conn.execute(
                """
                SELECT p.id, p.project_name, 'missing_report' as type, 1 as priority
                FROM projects p
                LEFT JOIN site_reports sr ON p.id = sr.project_id AND sr.report_date = ?
                WHERE p.status NOT IN ('Completed', 'On Hold')
                AND sr.id IS NULL
                LIMIT 3
                """,
                (today,)
            ).fetchall()
            
            for row in missing_reports:
                priorities.append({
                    "type": "missing_report",
                    "priority": 1,
                    "title": f"Daily Report Missing",
                    "description": f"No report submitted for {row['project_name']}",
                    "project_id": row["id"],
                    "action": "Submit Report",
                    "timestamp": datetime.now().isoformat(),
                })
        
        # Material requests pending (store keeper, project manager)
        if role in ("store_keeper", "project_manager", "admin", "super_admin"):
            pending_materials = conn.execute(
                """
                SELECT id, material_name, quantity, supplier
                FROM materials
                WHERE date_received IS NULL
                LIMIT 2
                """
            ).fetchall()
            
            for row in pending_materials:
                priorities.append({
                    "type": "pending_material",
                    "priority": 2,
                    "title": f"Material Pending Delivery",
                    "description": f"{row['material_name']} ({row['quantity']} units) from {row['supplier']}",
                    "material_id": row["id"],
                    "action": "Track Material",
                    "timestamp": datetime.now().isoformat(),
                })
        
        # Open issues (project manager, site engineer)
        if role in ("project_manager", "site_engineer", "admin", "super_admin"):
            open_issues = conn.execute(
                """
                SELECT id, title, priority, project_id FROM issues
                WHERE status = 'Open'
                ORDER BY priority = 'Critical' DESC, priority = 'High' DESC
                LIMIT 2
                """
            ).fetchall()
            
            for row in open_issues:
                priorities.append({
                    "type": "open_issue",
                    "priority": 1 if row["priority"] in ("Critical", "High") else 3,
                    "title": f"Open Issue: {row['title']}",
                    "description": f"Priority: {row['priority']}",
                    "issue_id": row["id"],
                    "action": "View Issue",
                    "timestamp": datetime.now().isoformat(),
                })
        
        # Low stock alerts (store keeper)
        if role in ("store_keeper", "project_manager", "admin", "super_admin"):
            low_stock = conn.execute(
                """
                SELECT m.id, m.material_name, m.balance, m.quantity, p.project_name
                FROM materials m
                JOIN projects p ON m.project_id = p.id
                WHERE m.balance < (m.quantity * 0.2) AND m.balance > 0
                LIMIT 2
                """
            ).fetchall()
            
            for row in low_stock:
                priorities.append({
                    "type": "low_stock",
                    "priority": 2,
                    "title": f"Low Stock Alert",
                    "description": f"{row['material_name']} down to {row['balance']} of {row['quantity']} units",
                    "material_id": row["id"],
                    "action": "Reorder",
                    "timestamp": datetime.now().isoformat(),
                })
        
        # Delayed tasks (project manager, site engineer)
        if role in ("project_manager", "site_engineer", "admin", "super_admin"):
            delayed_tasks = conn.execute(
                """
                SELECT t.id, t.title, p.project_name
                FROM tasks t
                JOIN projects p ON t.project_id = p.id
                WHERE t.status != 'Completed' AND t.progress_percent < 30
                ORDER BY t.created_at ASC
                LIMIT 2
                """
            ).fetchall()
            
            for row in delayed_tasks:
                priorities.append({
                    "type": "delayed_task",
                    "priority": 2,
                    "title": f"Task Behind Schedule",
                    "description": f"{row['title']} on {row['project_name']}",
                    "task_id": row["id"],
                    "action": "Expedite",
                    "timestamp": datetime.now().isoformat(),
                })
    
    # Sort by priority (1 = highest)
    priorities.sort(key=lambda x: (x["priority"], x["timestamp"]), reverse=False)
    return priorities[:5]  # Return top 5


def get_role_specific_alerts(user_id: int, role: str) -> list[dict]:
    """Get critical alerts specific to the user's role."""
    alerts = []
    
    with get_connection() as conn:
        # Equipment maintenance due (equipment officer, site engineer)
        if role in ("equipment_officer", "site_engineer", "admin", "super_admin"):
            maintenance_due = conn.execute(
                """
                SELECT id, equipment_name FROM equipment
                WHERE status = 'Maintenance Due'
                LIMIT 3
                """
            ).fetchall()
            
            for row in maintenance_due:
                alerts.append({
                    "severity": "warning",
                    "type": "maintenance",
                    "title": "Equipment Maintenance Due",
                    "message": f"{row['equipment_name']} requires scheduled maintenance",
                    "icon": "🔧",
                    "timestamp": datetime.now().isoformat(),
                })
        
        # Attendance anomalies (site engineer, project manager)
        if role in ("site_engineer", "project_manager", "admin", "super_admin"):
            today = datetime.now().strftime("%Y-%m-%d")
            low_attendance = conn.execute(
                """
                SELECT COUNT(*) as absent_count
                FROM attendance
                WHERE attendance_date = ? AND status = 'Absent'
                """,
                (today,)
            ).fetchone()
            
            if low_attendance["absent_count"] > 5:
                alerts.append({
                    "severity": "warning",
                    "type": "attendance",
                    "title": "High Absence Rate",
                    "message": f"{low_attendance['absent_count']} workers absent today",
                    "icon": "👥",
                    "timestamp": datetime.now().isoformat(),
                })
        
        # Budget overrun (project manager, admin)
        if role in ("project_manager", "admin", "super_admin"):
            projects = conn.execute(
                """
                SELECT id, project_name, budget FROM projects
                WHERE status NOT IN ('Completed', 'On Hold')
                AND budget > 0
                LIMIT 5
                """
            ).fetchall()
            
            for project in projects:
                total_cost = conn.execute(
                    """
                    SELECT COALESCE(SUM(CAST(quantity AS REAL)), 0) as total
                    FROM materials WHERE project_id = ?
                    """,
                    (project["id"],)
                ).fetchone()
                
                if total_cost["total"] > project["budget"] * 0.85:
                    alerts.append({
                        "severity": "critical" if total_cost["total"] > project["budget"] else "warning",
                        "type": "budget",
                        "title": "Budget Alert",
                        "message": f"{project['project_name']} approaching budget limit",
                        "icon": "💰",
                        "timestamp": datetime.now().isoformat(),
                    })
                    break  # Only show one budget alert
    
    return alerts[:5]  # Return top 5 alerts


def get_quick_actions(role: str) -> list[dict]:
    """Get role-specific quick action buttons."""
    actions = {
        "super_admin": [
            {"label": "Manage Users", "icon": "👤", "action": "admin_users"},
            {"label": "System Settings", "icon": "⚙️", "action": "admin_settings"},
            {"label": "View Audit Log", "icon": "📋", "action": "admin_audit"},
            {"label": "New Project", "icon": "📁", "action": "new_project"},
        ],
        "admin": [
            {"label": "New Project", "icon": "📁", "action": "new_project"},
            {"label": "Manage Users", "icon": "👤", "action": "admin_users"},
            {"label": "View Reports", "icon": "📊", "action": "view_reports"},
            {"label": "System Settings", "icon": "⚙️", "action": "admin_settings"},
        ],
        "project_manager": [
            {"label": "New Project", "icon": "📁", "action": "new_project"},
            {"label": "View Projects", "icon": "🗂️", "action": "view_projects"},
            {"label": "Approve Materials", "icon": "📦", "action": "approve_materials"},
            {"label": "Review Reports", "icon": "📄", "action": "review_reports"},
        ],
        "site_engineer": [
            {"label": "Submit Daily Report", "icon": "📝", "action": "submit_report"},
            {"label": "Record Attendance", "icon": "✓", "action": "record_attendance"},
            {"label": "Report Issue", "icon": "⚠️", "action": "report_issue"},
            {"label": "View Tasks", "icon": "✓", "action": "view_tasks"},
        ],
        "store_keeper": [
            {"label": "Issue Materials", "icon": "📦", "action": "issue_materials"},
            {"label": "Receive Stock", "icon": "📥", "action": "receive_stock"},
            {"label": "View Inventory", "icon": "📊", "action": "view_inventory"},
            {"label": "Low Stock Alert", "icon": "🚨", "action": "low_stock"},
        ],
        "equipment_officer": [
            {"label": "Record Equipment", "icon": "🔧", "action": "record_equipment"},
            {"label": "Schedule Maintenance", "icon": "📅", "action": "schedule_maintenance"},
            {"label": "View Equipment", "icon": "🔧", "action": "view_equipment"},
            {"label": "Maintenance Log", "icon": "📋", "action": "maintenance_log"},
        ],
        "contractor": [
            {"label": "Submit Daily Report", "icon": "📝", "action": "submit_report"},
            {"label": "View My Projects", "icon": "🗂️", "action": "view_projects"},
            {"label": "Report Issue", "icon": "⚠️", "action": "report_issue"},
            {"label": "Upload Photos", "icon": "📷", "action": "upload_photos"},
        ],
        "client": [
            {"label": "View My Projects", "icon": "🗂️", "action": "view_projects"},
            {"label": "View Reports", "icon": "📄", "action": "view_reports"},
            {"label": "Track Progress", "icon": "📊", "action": "track_progress"},
            {"label": "Messages", "icon": "💬", "action": "messages"},
        ],
        "consultant": [
            {"label": "View Projects", "icon": "🗂️", "action": "view_projects"},
            {"label": "Review Reports", "icon": "📄", "action": "review_reports"},
            {"label": "Analytics", "icon": "📊", "action": "analytics"},
            {"label": "Recommendations", "icon": "💡", "action": "recommendations"},
        ],
    }
    
    return actions.get(role, actions.get("contractor", []))


def get_user_dashboard_greeting(role: str, username: str) -> str:
    """Generate a role-appropriate greeting."""
    hour = datetime.now().hour
    time_of_day = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
    
    role_greetings = {
        "super_admin": f"{time_of_day}, System Administrator {username}! 👑 Welcome to the Command Center.",
        "admin": f"{time_of_day}, Administrator {username}! Welcome back to your operations dashboard.",
        "project_manager": f"{time_of_day}, Project Manager {username}! Here's your project status update.",
        "site_engineer": f"{time_of_day}, Site Engineer {username}! Ready for today's operations?",
        "store_keeper": f"{time_of_day}, Store Keeper {username}! Check your inventory status below.",
        "equipment_officer": f"{time_of_day}, Equipment Officer {username}! Fleet status ready for review.",
        "contractor": f"{time_of_day}, {username}! Ready to submit today's progress.",
        "client": f"{time_of_day}, {username}! Your project updates are below.",
        "consultant": f"{time_of_day}, {username}! Project insights and recommendations await.",
    }
    
    return role_greetings.get(role, f"{time_of_day}, {username}!")
