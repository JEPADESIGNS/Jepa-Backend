"""Dashboard helpers for the JEPA Site Manager experience."""

from jepa_site_manager.auth.permissions import (
    can_access_module,
    get_accessible_site_manager_actions,
    get_default_dashboard_module,
    get_role_title,
    normalize_role,
)
from jepa_site_manager.auth.roles import ROLE_ACCESS, get_site_manager_actions


__all__ = [
    "can_access_module",
    "get_accessible_site_manager_actions",
    "get_site_manager_actions",
    "get_default_dashboard_module",
    "get_role_title",
    "normalize_role",
    "ROLE_ACCESS",
]


def open_site_manager_module(parent, module_name: str, user_id: int | None = None, role: str | None = None) -> None:
    """Open one of the JEPA Site Manager module views from the dashboard."""
    module_name = (module_name or "").strip().lower()

    if module_name == "overview":
        from jepa_site_manager.core.hub import open_site_manager_hub

        open_site_manager_hub(parent, user_id=user_id, role=role)
        return

    if module_name == "projects":
        from jepa_site_manager.projects.project_view import open_project_manager

        open_project_manager(parent, user_id=user_id)
        return

    if module_name == "reports":
        from jepa_site_manager.reports.report_view import open_report_view

        open_report_view(parent, user_id=user_id)
        return

    if module_name == "materials":
        from jepa_site_manager.materials.material_view import open_material_view

        open_material_view(parent, user_id=user_id)
        return

    if module_name == "workforce":
        from jepa_site_manager.workforce.attendance_view import open_attendance_view

        open_attendance_view(parent, user_id=user_id)
        return

    if module_name in ("tasks", "task"):
        from jepa_site_manager.tasks.task_view import open_task_view

        open_task_view(parent, user_id=user_id)
        return

    if module_name == "equipment":
        from jepa_site_manager.equipment.equipment_view import open_equipment_view

        open_equipment_view(parent, user_id=user_id)
        return

    if module_name == "documents":
        from jepa_site_manager.documents.document_view import open_document_view

        open_document_view(parent, user_id=user_id)
        return

    if module_name == "issues":
        from jepa_site_manager.issues.issue_view import open_issue_view

        open_issue_view(parent, user_id=user_id)
        return

    if module_name == "notifications":
        from jepa_site_manager.notifications.notification_view import open_notifications_view

        open_notifications_view(parent, user_id=user_id)
        return

    if module_name == "administration":
        from jepa_site_manager.admin.admin_view import open_admin_workspace

        open_admin_workspace(parent, user_id=user_id)
        return

    raise ValueError(f"Unknown module '{module_name}'")
