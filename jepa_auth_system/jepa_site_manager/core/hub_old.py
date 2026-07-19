"""Overview hub for the JEPA Site Manager product surface."""

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
    "site_engineer": {
        "headline": "Today’s site priorities",
        "focus_items": [
            "Pending inspections",
            "Material requests",
            "Equipment availability",
            "Tasks due today",
        ],
        "recommended_actions": [
            "Field checklist",
            "Equipment status",
            "Material requests",
        ],
    },
    "admin": {
        "headline": "Project delivery overview",
        "focus_items": [
            "Delayed activities",
            "Budget utilisation",
            "Workforce deployment",
            "Open risks",
        ],
        "recommended_actions": [
            "Delivery review",
            "Budget watch",
            "Workforce deployment",
        ],
    },
    "client": {
        "headline": "Project visibility",
        "focus_items": [
            "Overall project progress",
            "Latest site photos",
            "Upcoming milestones",
            "Recent reports",
        ],
        "recommended_actions": [
            "Site reports",
            "Milestone review",
            "Approval tracker",
        ],
    },
}


def get_role_workspace_summary(role: str) -> dict:
    """Return the operational summary for a user role."""
    normalized = normalize_role(role)
    summary = ROLE_WORKSPACE_SUMMARIES.get(normalized, ROLE_WORKSPACE_SUMMARIES["client"])
    return {
        "headline": summary.get("headline", "Project visibility"),
        "focus_items": list(summary.get("focus_items", [])),
        "recommended_actions": list(summary.get("recommended_actions", [])),
    }


def _clear_frame(frame: tk.Widget) -> None:
    for child in frame.winfo_children():
        child.destroy()


def _panel(frame: tk.Frame, title: str, body: str, accent: str) -> None:
    card = tk.Frame(frame, bg="#0F172A", highlightthickness=1, highlightbackground=accent)
    card.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=6)
    tk.Label(card, text=title, fg="#F59E0B", bg="#0F172A", font=FONTS["label"]).pack(anchor="w", padx=12, pady=(12, 4))
    tk.Label(card, text=body, fg="#E5EEF8", bg="#0F172A", justify="left", wraplength=220, font=FONTS["small"]).pack(anchor="w", padx=12, pady=(0, 12))


def open_site_manager_hub(parent: tk.Misc | None = None, user_id: int | None = None, role: str | None = None) -> None:
    """Open a central JEPA Site Manager overview window for the main dashboards."""
    role_label = normalize_role(role)
    role_name = get_role_title(role_label)
    summary_hint = get_role_workspace_summary(role_label)
    theme = get_theme("dark")

    should_mainloop = parent is None
    if parent is None:
        window = tk.Tk()
    else:
        window = tk.Toplevel(parent)
    window.title("JEPA Site Manager — Operations Command Center")
    window.geometry("1320x820")
    window.configure(bg=theme["bg"])
    window.grid_rowconfigure(1, weight=1)
    window.grid_columnconfigure(1, weight=1)

    if Image is not None and ImageTk is not None:
        try:
            hero_image = Image.open(resolve_asset("dashboard_banner.png")).convert("RGBA")
            hero_photo = ImageTk.PhotoImage(hero_image.resize((260, 110), Image.Resampling.LANCZOS))
            logo = tk.Label(window, image=hero_photo, bg=theme["bg"])
            logo.image = hero_photo
            logo.grid(row=0, column=0, sticky="nw", padx=18, pady=18)
        except Exception:
            pass

    header_frame = tk.Frame(window, bg=theme["bg"])
    header_frame.grid(row=0, column=1, sticky="new", padx=(0, 18), pady=18)
    tk.Label(
        header_frame,
        text="JEPA SITE MANAGER",
        fg=theme["accent_hover"],
        bg=theme["bg"],
        font=("Segoe UI", 12, "bold"),
    ).pack(anchor="w")
    tk.Label(
        header_frame,
        text="Construction operations command center for daily delivery, field activity, materials, approvals, and reporting.",
        fg=theme["lbl_sub"],
        bg=theme["bg"],
        font=FONTS["small"],
    ).pack(anchor="w", pady=(4, 0))

    meta_frame = tk.Frame(header_frame, bg=theme["bg"])
    meta_frame.pack(anchor="w", pady=(10, 0), fill="x")
    tk.Label(
        meta_frame,
        text=f"Role: {role_name}",
        fg=theme["fg"],
        bg=theme["bg"],
        font=FONTS["body_bold"],
    ).pack(side="left")
    tk.Label(
        meta_frame,
        text=f"• {summary_hint['headline']}",
        fg=theme["lbl_sub"],
        bg=theme["bg"],
        font=FONTS["small"],
    ).pack(side="left", padx=(12, 0))

    body_frame = tk.Frame(window, bg=theme["bg"])
    body_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=18, pady=(0, 18))
    body_frame.grid_rowconfigure(0, weight=1)
    body_frame.grid_columnconfigure(1, weight=1)

    nav_frame = tk.Frame(body_frame, bg=theme["panel"], width=280)
    nav_frame.grid(row=0, column=0, sticky="nsw")
    nav_frame.grid_propagate(False)

    content_frame = tk.Frame(body_frame, bg=theme["panel2"])
    content_frame.grid(row=0, column=1, sticky="nsew", padx=(18, 0))
    content_frame.grid_rowconfigure(0, weight=1)
    content_frame.grid_columnconfigure(0, weight=1)

    tk.Label(nav_frame, text="Command Center", fg=theme["accent"], bg=theme["panel"], font=FONTS["h2"]).pack(anchor="w", padx=18, pady=(18, 6))
    tk.Label(
        nav_frame,
        text="One workspace for delivery, field operations, and project control.",
        fg=theme["lbl_sub"],
        bg=theme["panel"],
        justify="left",
        wraplength=246,
        font=FONTS["small"],
    ).pack(anchor="w", padx=18)

    accessible_actions = get_accessible_site_manager_actions(role_label)
    
    # ACTION BUTTONS for contractor command center
    action_buttons = [
        ("+ New Project", lambda: _open_full_module("projects")),
        ("+ Add User", lambda: _open_full_module("administration")),
        ("+ Create Report", lambda: _open_full_module("reports")),
        ("+ Material Request", lambda: _open_full_module("materials")),
        ("+ Attendance Review", lambda: _open_full_module("workforce")),
        ("⚠ View Alerts", lambda: _open_full_module("issues")),
    ]
    
    nav_buttons: dict[str, tk.Button] = {}
    selected_action = "overview"

    def _set_active(action: str) -> None:
        nonlocal selected_action
        selected_action = action
        for module_name, button in nav_buttons.items():
            if module_name == action:
                button.config(bg=theme["accent_hover"], fg="white")
            else:
                button.config(bg=theme["panel2"], fg=theme["fg"])
        _render_module(action)

    def _open_full_module(module_name: str) -> None:
        open_site_manager_module(window, module_name, user_id=user_id, role=role_label)

    def _render_overview() -> None:
        _clear_frame(content_frame)
        title_frame = tk.Frame(content_frame, bg=theme["panel2"])
        title_frame.pack(fill="x", padx=18, pady=(18, 0))
        tk.Label(title_frame, text="Daily Operations Brief", fg=theme["accent"], bg=theme["panel2"], font=FONTS["h2"]).pack(anchor="w")
        tk.Label(
            title_frame,
            text="A project-first landing page that keeps every construction workflow in one shell.",
            fg=theme["lbl_sub"],
            bg=theme["panel2"],
            font=FONTS["small"],
        ).pack(anchor="w", pady=(4, 0))

        metrics_data = get_admin_dashboard_metrics()
        active_projects = metrics_data["active_projects"]
        delayed_projects = metrics_data["delayed_projects"]
        missing_reports = metrics_data["missing_reports"]
        low_stock_alerts = metrics_data["low_stock_alerts"]
        workforce_on_site = metrics_data["workforce_on_site"]
        equipment_issues = metrics_data["equipment_issues"]
        recent_activity = metrics_data["recent_activity"]
        project_summary_data = metrics_data["project_summary"]

        top_summary = tk.Frame(content_frame, bg=theme["panel2"])
        top_summary.pack(fill="x", padx=18, pady=(12, 0))
        _panel(top_summary, "Executive Summary",
               f"{active_projects} active project workspaces, {workforce_on_site} crew on site, and {len(low_stock_alerts)} material alerts.",
               "#06B6D4")
        _panel(top_summary, "Project Health", f"{delayed_projects} delayed projects and {missing_reports} reports missing today.", "#F59E0B")
        _panel(top_summary, "Site Readiness", f"{equipment_issues} equipment issues reported and core workflows monitored.", "#22C55E")

        metrics_frame = tk.Frame(content_frame, bg=theme["panel2"])
        metrics_frame.pack(fill="x", padx=18, pady=(12, 0))
        metrics = [
            ("Active Sites", str(active_projects), "Live construction locations"),
            ("Delayed Projects", str(delayed_projects), "Needs attention"),
            ("Missing Reports", str(missing_reports), "Reports overdue today"),
            ("Materials Alerts", str(len(low_stock_alerts)), "Low-stock items"),
        ]
        for title, value, hint in metrics:
            card = tk.Frame(metrics_frame, bg=theme["panel"], bd=1, relief="solid")
            card.pack(side="left", fill="both", expand=True, padx=(0, 8))
            tk.Label(card, text=title, fg=theme["accent"], bg=theme["panel"], font=FONTS["label"]).pack(anchor="w", padx=12, pady=(12, 4))
            tk.Label(card, text=value, fg=theme["fg"], bg=theme["panel"], font=("Segoe UI", 20, "bold")).pack(anchor="w", padx=12)
            tk.Label(card, text=hint, fg=theme["lbl_sub"], bg=theme["panel"], font=FONTS["small"]).pack(anchor="w", padx=12, pady=(0, 12))

        quick_frame = tk.Frame(content_frame, bg=theme["panel2"])
        quick_frame.pack(fill="x", padx=18, pady=(12, 16))
        for chip in summary_hint.get("recommended_actions", []):
            tk.Label(
                quick_frame,
                text=chip,
                fg=theme["fg"],
                bg=theme["panel"],
                bd=1,
                relief="solid",
                padx=10,
                pady=4,
                font=FONTS["small_bold"],
            ).pack(side="left", padx=(0, 8), pady=(0, 4))

        alert_body = []
        if missing_reports:
            alert_body.append(f"{missing_reports} missing daily report(s)")
        if delayed_projects:
            alert_body.append(f"{delayed_projects} delayed project(s)")
        if low_stock_alerts:
            alert_body.append(f"{len(low_stock_alerts)} low stock alert(s)")
        if not alert_body:
            alert_body.append("No critical alerts at this time.")

        alert_frame = tk.Frame(content_frame, bg=theme["panel"], bd=1, relief="solid")
        alert_frame.pack(fill="x", padx=18, pady=(0, 18))
        tk.Label(alert_frame, text="Alerts & Watchlist", fg=theme["accent"], bg=theme["panel"], font=FONTS["h3"]).pack(anchor="w", padx=12, pady=(12, 6))
        tk.Label(alert_frame, text=" • ".join(alert_body), fg=theme["fg"], bg=theme["panel"], justify="left", wraplength=860, font=FONTS["body"]).pack(anchor="w", padx=12, pady=(0, 12))

        projects_frame = tk.Frame(content_frame, bg=theme["panel2"])
        projects_frame.pack(fill="x", padx=18, pady=(0, 18))
        tk.Label(projects_frame, text="Project Health", fg=theme["accent"], bg=theme["panel2"], font=FONTS["h3"]).pack(anchor="w", padx=12, pady=(0, 8))
        if project_summary_data:
            project_cards = tk.Frame(projects_frame, bg=theme["panel2"])
            project_cards.pack(fill="x")
            for project in project_summary_data[:3]:
                card = tk.Frame(project_cards, bg=theme["panel"], bd=1, relief="solid")
                card.pack(side="left", fill="both", expand=True, padx=(0, 8))
                tk.Label(card, text=project["project_name"], fg=theme["accent"], bg=theme["panel"], font=FONTS["label"]).pack(anchor="w", padx=12, pady=(12, 4))
                tk.Label(card, text=f"Status: {project['status']}", fg=theme["fg"], bg=theme["panel"], font=FONTS["small_bold"]).pack(anchor="w", padx=12)
                tk.Label(card, text=f"Progress: {int(project['progress_percent'])}%", fg=theme["fg"], bg=theme["panel"], font=FONTS["small"]).pack(anchor="w", padx=12, pady=(4, 8))
                tk.Label(card, text=f"Last report: {project.get('last_report_date') or 'None'}", fg=theme["lbl_sub"], bg=theme["panel"], font=FONTS["small"]).pack(anchor="w", padx=12, pady=(0, 12))
        else:
            tk.Label(projects_frame, text="No current project health snapshots are available.", fg=theme["lbl_sub"], bg=theme["panel2"], font=FONTS["small"]).pack(anchor="w", padx=12, pady=(0, 8))

        activity_frame = tk.Frame(content_frame, bg=theme["panel"], bd=1, relief="solid")
        activity_frame.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        tk.Label(activity_frame, text="Recent Activity Feed", fg=theme["accent"], bg=theme["panel"], font=FONTS["h3"]).pack(anchor="w", padx=12, pady=(12, 6))
        if recent_activity:
            for event in recent_activity[:8]:
                tk.Label(activity_frame, text=f"{event['timestamp']} — {event['subject']} — {event['action']} {event.get('detail') or ''}", fg=theme["fg"], bg=theme["panel"], anchor="w", justify="left", wraplength=860, font=FONTS["small"]).pack(fill="x", padx=12, pady=(0, 4))
        else:
            tk.Label(activity_frame, text="No recent activity has been recorded yet.", fg=theme["lbl_sub"], bg=theme["panel"], font=FONTS["small"]).pack(anchor="w", padx=12, pady=(0, 8))

        tk.Button(
            activity_frame,
            text="Open Full Project Workspace",
            command=lambda: _open_full_module("projects"),
            bg=theme["accent"],
            fg="white",
            font=FONTS["body_bold"],
            bd=0,
            cursor="hand2",
        ).pack(anchor="w", padx=12, pady=(10, 14))

    def _render_projects() -> None:
        _clear_frame(content_frame)
        tk.Label(content_frame, text="Project Workspace", fg=theme["accent"], bg=theme["panel2"], font=FONTS["h2"]).pack(anchor="w", padx=18, pady=(18, 6))
        tk.Label(
            content_frame,
            text="Browse your most recent projects and open the full project workspace when you need to take action.",
            fg=theme["lbl_sub"],
            bg=theme["panel2"],
            font=FONTS["small"],
        ).pack(anchor="w", padx=18)

        projects = list_projects()
        project_count = len(projects)
        summary_card = tk.Frame(content_frame, bg=theme["panel"], bd=1, relief="solid")
        summary_card.pack(fill="x", padx=18, pady=(14, 8))
        tk.Label(summary_card, text=f"{project_count} active projects", fg=theme["fg"], bg=theme["panel"], font=FONTS["body_bold"]).pack(anchor="w", padx=12, pady=(12, 4))
        tk.Label(summary_card, text="A snapshot of the latest project data pulled directly from the site manager.", fg=theme["lbl_sub"], bg=theme["panel"], font=FONTS["small"]).pack(anchor="w", padx=12, pady=(0, 12))

        columns = ("id", "name", "client", "location", "status")
        tree = ttk.Treeview(content_frame, columns=columns, show="headings", height=8)
        for heading in columns:
            tree.heading(heading, text=heading.replace("_", " ").title())
        tree.pack(fill="both", expand=True, padx=18, pady=(0, 8))

        for row in projects[:8]:
            tree.insert("", "end", values=(row["id"], row["project_name"], row["client"] or "—", row["location"] or "—", row["status"]))

        if project_count == 0:
            tk.Label(content_frame, text="No projects are available yet. Use the project workspace to create the first one.", fg=theme["lbl_sub"], bg=theme["panel2"], font=FONTS["small"]).pack(anchor="w", padx=18, pady=(8, 0))

        tk.Button(
            content_frame,
            text="Open Full Project Workspace",
            command=lambda: _open_full_module("projects"),
            bg=theme["accent"],
            fg="white",
            font=FONTS["body_bold"],
            bd=0,
            cursor="hand2",
        ).pack(anchor="w", padx=18, pady=(10, 14))

    def _render_reports() -> None:
        _clear_frame(content_frame)
        tk.Label(content_frame, text="Site Reports", fg=theme["accent"], bg=theme["panel2"], font=FONTS["h2"]).pack(anchor="w", padx=18, pady=(18, 6))
        tk.Label(
            content_frame,
            text="Access and create reporting assets for clients, regulators, and delivery teams.",
            fg=theme["lbl_sub"],
            bg=theme["panel2"],
            font=FONTS["small"],
        ).pack(anchor="w", padx=18)
        tk.Label(
            content_frame,
            text="Reports are the single source of truth for approvals, audits, and progress status across all sites.",
            fg=theme["fg"],
            bg=theme["panel2"],
            wraplength=860,
            justify="left",
            font=FONTS["body"],
        ).pack(anchor="w", padx=18, pady=(14, 0))
        tk.Button(
            content_frame,
            text="Open Reports Module",
            command=lambda: _open_full_module("reports"),
            bg=theme["accent"],
            fg="white",
            font=FONTS["body_bold"],
            bd=0,
            cursor="hand2",
        ).pack(anchor="w", padx=18, pady=(16, 0))

    def _render_materials() -> None:
        _clear_frame(content_frame)
        tk.Label(content_frame, text="Store & Materials", fg=theme["accent"], bg=theme["panel2"], font=FONTS["h2"]).pack(anchor="w", padx=18, pady=(18, 6))
        tk.Label(
            content_frame,
            text="Track inventory requests, receipt confirmations, and material capacities in a single site command surface.",
            fg=theme["lbl_sub"],
            bg=theme["panel2"],
            font=FONTS["small"],
        ).pack(anchor="w", padx=18)
        tk.Button(
            content_frame,
            text="Open Materials Module",
            command=lambda: _open_full_module("materials"),
            bg=theme["accent"],
            fg="white",
            font=FONTS["body_bold"],
            bd=0,
            cursor="hand2",
        ).pack(anchor="w", padx=18, pady=(16, 0))

    def _render_workforce() -> None:
        _clear_frame(content_frame)
        tk.Label(content_frame, text="Attendance & Workforce", fg=theme["accent"], bg=theme["panel2"], font=FONTS["h2"]).pack(anchor="w", padx=18, pady=(18, 6))
        tk.Label(
            content_frame,
            text="Monitor crew attendance, daily check-ins, and labour deployment from one operational shell.",
            fg=theme["lbl_sub"],
            bg=theme["panel2"],
            font=FONTS["small"],
        ).pack(anchor="w", padx=18)
        tk.Button(
            content_frame,
            text="Open Workforce Module",
            command=lambda: _open_full_module("workforce"),
            bg=theme["accent"],
            fg="white",
            font=FONTS["body_bold"],
            bd=0,
            cursor="hand2",
        ).pack(anchor="w", padx=18, pady=(16, 0))

    def _render_equipment() -> None:
        _clear_frame(content_frame)
        tk.Label(content_frame, text="Equipment & Assets", fg=theme["accent"], bg=theme["panel2"], font=FONTS["h2"]).pack(anchor="w", padx=18, pady=(18, 6))
        tk.Label(
            content_frame,
            text="Review equipment status, availability, and planned mobilization for site activities.",
            fg=theme["lbl_sub"],
            bg=theme["panel2"],
            font=FONTS["small"],
        ).pack(anchor="w", padx=18)
        tk.Button(
            content_frame,
            text="Open Equipment Module",
            command=lambda: _open_full_module("equipment"),
            bg=theme["accent"],
            fg="white",
            font=FONTS["body_bold"],
            bd=0,
            cursor="hand2",
        ).pack(anchor="w", padx=18, pady=(16, 0))

    def _render_boq() -> None:
        _clear_frame(content_frame)
        tk.Label(content_frame, text="BOQ & Costs", fg=theme["accent"], bg=theme["panel2"], font=FONTS["h2"]).pack(anchor="w", padx=18, pady=(18, 6))
        tk.Label(
            content_frame,
            text="Open the bill of quantities module to connect budgets with project execution as needed.",
            fg=theme["lbl_sub"],
            bg=theme["panel2"],
            font=FONTS["small"],
        ).pack(anchor="w", padx=18)
        tk.Button(
            content_frame,
            text="Open BOQ Module",
            command=lambda: _open_full_module("boq"),
            bg=theme["accent"],
            fg="white",
            font=FONTS["body_bold"],
            bd=0,
            cursor="hand2",
        ).pack(anchor="w", padx=18, pady=(16, 0))

    def _render_documents() -> None:
        _clear_frame(content_frame)
        tk.Label(content_frame, text="Documents & Submittals", fg=theme["accent"], bg=theme["panel2"], font=FONTS["h2"]).pack(anchor="w", padx=18, pady=(18, 6))
        tk.Label(
            content_frame,
            text="Review drawings, permits, contracts, and submittal packages in one place.",
            fg=theme["lbl_sub"],
            bg=theme["panel2"],
            font=FONTS["small"],
        ).pack(anchor="w", padx=18)
        tk.Button(
            content_frame,
            text="Open Documents Module",
            command=lambda: _open_full_module("documents"),
            bg=theme["accent"],
            fg="white",
            font=FONTS["body_bold"],
            bd=0,
            cursor="hand2",
        ).pack(anchor="w", padx=18, pady=(16, 0))

    def _render_issues() -> None:
        _clear_frame(content_frame)
        tk.Label(content_frame, text="Issues & Observations", fg=theme["accent"], bg=theme["panel2"], font=FONTS["h2"]).pack(anchor="w", padx=18, pady=(18, 6))
        tk.Label(
            content_frame,
            text="Capture safety, quality, and delivery issues with a clear project workflow.",
            fg=theme["lbl_sub"],
            bg=theme["panel2"],
            font=FONTS["small"],
        ).pack(anchor="w", padx=18)
        tk.Button(
            content_frame,
            text="Open Issues Module",
            command=lambda: _open_full_module("issues"),
            bg=theme["accent"],
            fg="white",
            font=FONTS["body_bold"],
            bd=0,
            cursor="hand2",
        ).pack(anchor="w", padx=18, pady=(16, 0))

    def _render_notifications() -> None:
        _clear_frame(content_frame)
        tk.Label(content_frame, text="Notifications & Alerts", fg=theme["accent"], bg=theme["panel2"], font=FONTS["h2"]).pack(anchor="w", padx=18, pady=(18, 6))
        tk.Label(
            content_frame,
            text="Keep your team in sync with alerts, reminders, and operational messages.",
            fg=theme["lbl_sub"],
            bg=theme["panel2"],
            font=FONTS["small"],
        ).pack(anchor="w", padx=18)
        tk.Button(
            content_frame,
            text="Open Notifications Module",
            command=lambda: _open_full_module("notifications"),
            bg=theme["accent"],
            fg="white",
            font=FONTS["body_bold"],
            bd=0,
            cursor="hand2",
        ).pack(anchor="w", padx=18, pady=(16, 0))

    def _render_administration() -> None:
        _clear_frame(content_frame)
        tk.Label(content_frame, text="Administration Workspace", fg=theme["accent"], bg=theme["panel2"], font=FONTS["h2"]).pack(anchor="w", padx=18, pady=(18, 6))
        tk.Label(
            content_frame,
            text="Manage user access, system settings, and audit log visibility from one interface.",
            fg=theme["lbl_sub"],
            bg=theme["panel2"],
            font=FONTS["small"],
        ).pack(anchor="w", padx=18)
        tk.Button(
            content_frame,
            text="Open Administration Module",
            command=lambda: _open_full_module("administration"),
            bg=theme["accent"],
            fg="white",
            font=FONTS["body_bold"],
            bd=0,
            cursor="hand2",
        ).pack(anchor="w", padx=18, pady=(16, 0))

    def _render_analytics() -> None:
        _clear_frame(content_frame)
        tk.Label(content_frame, text="Analytics & Insights", fg=theme["accent"], bg=theme["panel2"], font=FONTS["h2"]).pack(anchor="w", padx=18, pady=(18, 6))
        tk.Label(
            content_frame,
            text="Bring delivery metrics and project trends into one place for tactical decision making.",
            fg=theme["lbl_sub"],
            bg=theme["panel2"],
            font=FONTS["small"],
        ).pack(anchor="w", padx=18)
        tk.Button(
            content_frame,
            text="Open Analytics Module",
            command=lambda: _open_full_module("analytics"),
            bg=theme["accent"],
            fg="white",
            font=FONTS["body_bold"],
            bd=0,
            cursor="hand2",
        ).pack(anchor="w", padx=18, pady=(16, 0))

    module_renderers = {
        "overview": _render_overview,
        "projects": _render_projects,
        "reports": _render_reports,
        "materials": _render_materials,
        "workforce": _render_workforce,
        "equipment": _render_equipment,
        "boq": _render_boq,
        "documents": _render_documents,
        "issues": _render_issues,
        "notifications": _render_notifications,
        "administration": _render_administration,
        "analytics": _render_analytics,
    }

    def _render_module(module_name: str) -> None:
        renderer = module_renderers.get(module_name, _render_overview)
        renderer()

    tk.Label(nav_frame, text="Command Center", fg=theme["accent_hover"], bg=theme["panel"], font=FONTS["label"]).pack(anchor="w", padx=18, pady=(18, 6))

    for button_text, button_cmd in action_buttons:
        btn = tk.Button(
            nav_frame,
            text=button_text,
            command=button_cmd,
            anchor="w",
            justify="left",
            bd=0,
            relief="flat",
            padx=18,
            pady=12,
            bg=theme["panel2"],
            fg=theme["fg"],
            cursor="hand2",
            font=FONTS["body_bold"],
        )
        btn.pack(fill="x", padx=12, pady=(0, 6))

    tk.Frame(nav_frame, bg=theme["panel"], height=1).pack(fill="x", padx=18, pady=(12, 12))
    
    # Navigation items below divider
    tk.Label(nav_frame, text="Workspace", fg=theme["accent_hover"], bg=theme["panel"], font=FONTS["label"]).pack(anchor="w", padx=18, pady=(12, 6))

    for label, module_name in accessible_actions:
        btn = tk.Button(
            nav_frame,
            text=label,
            command=lambda m=module_name: _set_active(m),
            anchor="w",
            justify="left",
            bd=0,
            relief="flat",
            padx=18,
            pady=10,
            bg=theme["panel2"],
            fg=theme["fg"],
            cursor="hand2",
            font=FONTS["body"],
        )
        btn.pack(fill="x", padx=12, pady=(0, 4))
        nav_buttons[module_name] = btn

    tk.Frame(nav_frame, bg=theme["panel"], height=1).pack(fill="x", padx=18, pady=(12, 12))
    tk.Button(
        nav_frame,
        text="Open full shell modules",
        command=lambda: _open_full_module(selected_action if selected_action != "overview" else "projects"),
        bg=theme["accent"],
        fg="white",
        bd=0,
        cursor="hand2",
        font=FONTS["small_bold"],
    ).pack(fill="x", padx=18, pady=(0, 4), ipady=10)

    _set_active(get_default_dashboard_module(role_label))

    if should_mainloop:
        window.mainloop()
