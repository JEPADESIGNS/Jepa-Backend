"Overview hub for the JEPA Site Manager product surface."

import tkinter as tk
from tkinter import ttk
from datetime import datetime

try:
    from PIL import Image, ImageTk
except ImportError:  # pragma: no cover
    Image = None
    ImageTk = None

from ui.components import resolve_asset
from ui.themes import FONTS, get_theme
from dashboard import (
    normalize_role,
    get_role_title,
    get_accessible_site_manager_actions,
    get_default_dashboard_module,
    open_site_manager_module,
)
from jepa_site_manager.projects.project_service import list_projects
from jepa_site_manager.core.dashboard_service import get_admin_dashboard_metrics


ROLE_WORKSPACE_SUMMARIES = {
    site_engineer: {
        headline: Today'''s site priorities,
        focus_items: [
            Pending inspections,
            Material requests,
            Equipment availability,
            Tasks due today,
        ],
        recommended_actions: [
            Field checklist,
            Equipment status,
            Material requests,
        ],
    },
    admin: {
        headline: Project delivery overview,
        focus_items: [
            Delayed activities,
            Budget utilisation,
            Workforce deployment,
            Open risks,
        ],
        recommended_actions: [
            Delivery review,
            Budget watch,
            Workforce deployment,
        ],
    },
    client: {
        headline: Project visibility,
        focus_items: [
            Overall project progress,
            Latest site photos,
            Upcoming milestones,
            Recent reports,
        ],
        recommended_actions: [
            Site reports,
            Milestone review,
            Approval tracker,
        ],
    },
}


def get_role_workspace_summary(role: str) -> dict:
    "Return the operational summary for a user role."
    normalized = normalize_role(role)
    summary = ROLE_WORKSPACE_SUMMARIES.get(normalized, ROLE_WORKSPACE_SUMMARIES[client])
    return {
        headline: summary.get(headline, Project visibility),
        focus_items: list(summary.get(focus_items, [])),
        recommended_actions: list(summary.get(recommended_actions, [])),
    }


def _clear_frame(frame: tk.Widget) -> None:
    for child in frame.winfo_children():
        child.destroy()
