"""
dashboard/admin_dashboard.py — Admin management panel with user controls and 2FA resets.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from database.db import get_connection
from ui.themes import FONTS, get_theme
from ui.components import resolve_asset
from utils.logger import log_activity
from dashboard import get_site_manager_actions, open_site_manager_module
from jepa_site_manager.core.dashboard_service import get_admin_dashboard_metrics


def format_activity_rows(rows):
    """Create readable summaries for recent audit-log entries."""
    formatted = []
    for row in rows:
        action = str(row.get("action") or "Activity")
        username = str(row.get("username") or "System")
        details = str(row.get("details") or "").strip()
        summary = action if not details else f"{action} — {details}"
        formatted.append({
            "timestamp": str(row.get("timestamp") or ""),
            "username": username,
            "action": action,
            "details": details,
            "summary": summary,
        })
    return formatted


def filter_activity_logs(rows, query: str):
    """Filter recent activity rows by username, action, or details."""
    text = (query or "").strip().lower()
    if not text:
        return list(rows)

    filtered = []
    for row in rows:
        searchable = " ".join([
            str(row.get("username", "")),
            str(row.get("action", "")),
            str(row.get("details", "")),
            str(row.get("timestamp", "")),
        ]).lower()
        if text in searchable:
            filtered.append(row)
    return filtered


def summarize_live_events(rows):
    """Summarize recent registrations and login events for the live monitor."""
    summary = {
        "registrations": 0,
        "logins": 0,
        "latest": "No recent live events",
        "events": len(rows or []),
    }

    latest_items = []
    for row in rows or []:
        action = str(row.get("action") or "").lower()
        if "register" in action or "registration" in action:
            summary["registrations"] += 1
        if "login" in action:
            summary["logins"] += 1

        username = str(row.get("username") or "System").strip()
        if username and username.lower() != "none":
            latest_items.append(f"{username} • {str(row.get('action') or 'Activity')}")

    if latest_items:
        summary["latest"] = " | ".join(latest_items[:4])

    return summary


def format_live_event_row(row):
    """Return a readable live-event entry with current device context."""
    timestamp = str(row.get("timestamp") or "").strip()
    username = str(row.get("username") or "System").strip() or "System"
    action = str(row.get("action") or "Activity").strip() or "Activity"
    details = str(row.get("details") or "").strip()
    ip_address = str(row.get("ip_address") or "").strip()

    label_parts = [username, action]
    if details:
        label_parts.append(details)
    if ip_address:
        label_parts.append(f"Device/IP: {ip_address}")

    return {
        "timestamp": timestamp,
        "label": " • ".join(label_parts),
        "summary": f"{timestamp} • {action}" if timestamp else action,
    }


def toggle_panel_visibility(visible: bool) -> bool:
    """Return the opposite visibility state for a collapsible panel."""
    return not visible


def admin_dashboard(user_id: int, username: str, saved_theme: str = "dark"):
    t = get_theme(saved_theme)

    dash = tk.Tk()
    dash.title("JEPA Site Manager — Admin Workspace")
    dash.geometry("1220x760")
    dash.resizable(True, True)
    dash.configure(bg=t["bg"])

    try:
        dash.iconbitmap(str(resolve_asset("app_icon.ico")))
    except Exception:
        pass

    # ── Treeview style ─────────────────────────────────────────────────────────
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Admin.Treeview",
                    background=t["panel2"],
                    fieldbackground=t["panel2"],
                    foreground=t["fg"],
                    rowheight=30)
    style.configure("Admin.Treeview.Heading",
                    background=t["panel"],
                    foreground=t["fg"],
                    font=("Segoe UI", 9, "bold"))
    style.map("Admin.Treeview", background=[("selected", t["accent"])], foreground=[("selected", "white")])

    # ── Header ─────────────────────────────────────────────────────────────────
    hdr = tk.Frame(dash, bg=t["bg"])
    hdr.pack(fill="x", padx=25, pady=(18, 6))

    quick_actions = {"show_activity": False, "show_details": True}

    tk.Label(hdr, text="JEPA WORKSPACE BRIEF", font=("Segoe UI", 12, "bold"),
             fg=t["accent_hover"], bg=t["bg"]).pack(side="left")
    tk.Label(hdr, text="Delivery • Materials • Workforce • Site approvals • Operations overview",
             fg=t["lbl_sub"], bg=t["bg"], font=FONTS["small"]).pack(side="left", padx=(12, 0))

    workspace_banner = tk.Frame(dash, bg="#111827", highlightthickness=1, highlightbackground="#1F2937")
    workspace_banner.pack(fill="x", padx=25, pady=(0, 6))
    tk.Label(workspace_banner, text="UPDATED ADMIN WORKSPACE", fg="#FDE68A", bg="#111827",
             font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12, pady=(8, 2))
    tk.Label(workspace_banner,
             text="This admin view now emphasizes project delivery, site operations, material flow, and field activity in one workspace.",
             fg="#E5E7EB", bg="#111827", justify="left", wraplength=980, font=FONTS["small"]).pack(anchor="w", padx=12, pady=(0, 10))

    header_actions = tk.Frame(hdr, bg=t["bg"])
    header_actions.pack(side="right", pady=5)

    action_btn = tk.Button(header_actions, text="Actions", bg="#0EA5E9", fg="white",
                           font=FONTS["small_bold"], bd=0, cursor="hand2")
    action_btn.pack(side="left", ipady=3)

    activity_toggle = tk.Button(header_actions, text="Recent Activity", bg="#334155", fg="#F8FAFC",
                                font=FONTS["small_bold"], bd=0, cursor="hand2")
    activity_toggle.pack(side="left", padx=(6, 0), ipady=3)

    details_toggle = tk.Button(header_actions, text="Workspace Details", bg="#8B5CF6", fg="white",
                                font=FONTS["small_bold"], bd=0, cursor="hand2")
    details_toggle.pack(side="left", padx=(6, 0), ipady=3)

    lbl_admin = tk.Label(hdr, text=f"Admin: {username.upper()} (ID: #{user_id})",
                         font=FONTS["small_bold"], fg=t["fg"], bg=t["bg"])
    lbl_admin.pack(side="right", padx=(10, 0), pady=5)

    badge = tk.Label(hdr, text="ONLINE", fg=t["success"], bg=t["panel2"], bd=1, relief="solid",
                     font=("Segoe UI", 8, "bold"), padx=8, pady=2)
    badge.pack(side="right", padx=(0, 10), pady=5)

    metrics = tk.Frame(dash, bg=t["bg"])
    metrics.pack(fill="x", padx=25, pady=(0, 8))

    def _mini_card(parent, title, value, color, accent):
        card = tk.Frame(parent, bg=color, highlightthickness=1, highlightbackground=accent)
        card.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=2)
        tk.Label(card, text=title, fg="#F8FAFC", bg=color, font=FONTS["small_bold"]).pack(anchor="w", padx=10, pady=(8, 0))
        tk.Label(card, text=value, fg="#FFFFFF", bg=color, font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=10, pady=(0, 8))
        return card

    metrics_data = get_admin_dashboard_metrics()
    _mini_card(metrics, "ACTIVE WORKSPACE", f"{metrics_data['active_projects']} active projects", "#1E293B", "#334155")
    _mini_card(metrics, "FIELD CREW", f"{metrics_data['workforce_on_site']} on site", "#0F766E", "#14B8A6")
    _mini_card(metrics, "MATERIAL ALERTS", f"{len(metrics_data['low_stock_alerts'])} low-stock alerts", "#312E81", "#6366F1")
    _mini_card(metrics, "DELAYED PROJECTS", f"{metrics_data['delayed_projects']} delayed", "#1F2937", "#F59E0B")

    project_summary = metrics_data.get("project_summary", [])
    summary_panel = tk.Frame(dash, bg="#111827", highlightthickness=1, highlightbackground="#1F2937")
    summary_panel.pack(fill="x", padx=25, pady=(0, 8))
    tk.Label(summary_panel, text="Active Project Snapshots", fg="#FDE68A", bg="#111827",
             font=FONTS["small_bold"]).pack(anchor="w", padx=12, pady=(10, 2))
    tk.Label(summary_panel,
             text="Live project status pulled from active delivery workspaces, recent reports, and field updates.",
             fg="#E5E7EB", bg="#111827", justify="left", wraplength=980, font=FONTS["small"]).pack(anchor="w", padx=12, pady=(0, 8))

    snapshot_row = tk.Frame(summary_panel, bg="#111827")
    snapshot_row.pack(fill="x", padx=12, pady=(0, 10))

    def _project_snapshot_card(project: dict):
        card = tk.Frame(snapshot_row, bg="#0F172A", highlightthickness=1, highlightbackground="#4F46E5")
        card.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(card, text=project["project_name"], fg="#F8FAFC", bg="#0F172A", font=FONTS["small_bold"]).pack(anchor="w", padx=10, pady=(8, 0))
        tk.Label(card,
                 text=f"Status: {project['status']} • Progress: {int(project['progress_percent'])}%\nLast report: {project.get('last_report_date') or 'None'}",
                 fg="#CBD5E1", bg="#0F172A", justify="left", wraplength=240, font=FONTS["small"]).pack(anchor="w", padx=10, pady=(6, 10))

    if project_summary:
        for project in project_summary[:3]:
            _project_snapshot_card(project)
    else:
        tk.Label(snapshot_row, text="No active project snapshots available yet.", fg="#CBD5E1", bg="#111827", font=FONTS["small"]).pack(anchor="w", padx=10, pady=10)

    # ── Project Focus Panel ──────────────────────────────────────────────────
    focus_panel = tk.Frame(dash, bg="#111827", highlightthickness=1, highlightbackground="#1F2937")
    focus_panel.pack(fill="x", padx=25, pady=(0, 8))

    tk.Label(focus_panel, text="PROJECT WORKSPACE FOCUS", fg="#FDE68A", bg="#111827",
             font=FONTS["small_bold"]).pack(anchor="w", padx=12, pady=(10, 2))
    tk.Label(focus_panel,
             text="This admin view now centres on project delivery, materials, approvals, and field activity instead of the old account table.",
             fg="#E5E7EB", bg="#111827", justify="left", wraplength=980, font=FONTS["small"]).pack(anchor="w", padx=12, pady=(0, 8))

    focus_grid = tk.Frame(focus_panel, bg="#111827")
    focus_grid.pack(fill="x", padx=12, pady=(0, 10))

    def _focus_card(title: str, body: str, accent: str):
        card = tk.Frame(focus_grid, bg="#0F172A", highlightthickness=1, highlightbackground=accent)
        card.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(card, text=title, fg="#F8FAFC", bg="#0F172A", font=FONTS["small_bold"]).pack(anchor="w", padx=10, pady=(8, 0))
        tk.Label(card, text=body, fg="#CBD5E1", bg="#0F172A", justify="left", wraplength=220, font=FONTS["small"]).pack(anchor="w", padx=10, pady=(0, 8))

    _focus_card("Project Delivery", "North Tower Expansion • 68% complete • 2 milestones due", "#22C55E")
    _focus_card("Material Flow", "Cement, steel, and site consumables tracked by current shift", "#06B6D4")
    _focus_card("Field Activity", "Attendance, equipment readiness, and recent reports in one view", "#F59E0B")
    _focus_card("Approvals", "Daily approvals, risks, and contractor updates for the site", "#8B5CF6")

    details_panel = tk.Frame(dash, bg="#111827", highlightthickness=1, highlightbackground="#1F2937")
    details_panel.pack(fill="x", padx=25, pady=(0, 8))

    tk.Label(details_panel, text="Operations workspace", fg="#F8FAFC", bg="#111827",
             font=FONTS["small_bold"]).pack(anchor="w", padx=12, pady=(10, 2))
    details_lbl = tk.Label(details_panel, text="This admin workspace now highlights delivery status, material usage, approvals, and site activity in one operations view.",
                           fg="#CBD5E1", bg="#111827", justify="left", wraplength=980,
                           font=FONTS["small"])
    details_lbl.pack(anchor="w", padx=12, pady=(0, 10))

    activity_panel = tk.Frame(dash, bg="#111827", highlightthickness=1, highlightbackground="#1F2937")
    activity_panel.pack(fill="x", padx=25, pady=(0, 12))
    activity_panel.pack_forget()

    tk.Label(activity_panel, text="Recent Activity Audit Trail", fg="#F8FAFC", bg="#111827",
             font=FONTS["small_bold"]).pack(anchor="w", padx=12, pady=(10, 4))

    live_monitor_panel = tk.Frame(dash, bg="#111827", highlightthickness=1, highlightbackground="#1F2937")
    live_monitor_panel.pack(fill="x", padx=25, pady=(0, 12))

    live_monitor_header = tk.Frame(live_monitor_panel, bg="#111827")
    live_monitor_header.pack(fill="x", padx=12, pady=(10, 6))

    tk.Label(live_monitor_header, text="Live Operations & Device Monitor", fg="#F8FAFC", bg="#111827",
             font=FONTS["small_bold"]).pack(side="left")
    live_monitor_hint = tk.Label(live_monitor_header, text="Live feed from site activity, approvals, logins, and device events.",
                                 fg="#CBD5E1", bg="#111827", font=FONTS["small"])
    live_monitor_hint.pack(side="left", padx=(8, 0))

    live_summary_bar = tk.Frame(live_monitor_panel, bg="#111827")
    live_summary_bar.pack(fill="x", padx=12, pady=(0, 8))

    live_summary_text = tk.Label(live_summary_bar, text="Monitoring recent activity…",
                                 fg="#E2E8F0", bg="#111827", justify="left", wraplength=980,
                                 font=FONTS["small"])
    live_summary_text.pack(anchor="w")

    live_event_tree = ttk.Treeview(live_monitor_panel, columns=("timestamp", "event", "details"),
                                   show="headings", height=6, style="Admin.Treeview")
    live_event_tree.heading("timestamp", text="TIME")
    live_event_tree.heading("event", text="EVENT")
    live_event_tree.heading("details", text="DEVICE / DETAILS")
    live_event_tree.column("timestamp", width=140, anchor="w")
    live_event_tree.column("event", width=170, anchor="w")
    live_event_tree.column("details", width=520, anchor="w")
    live_event_tree.pack(fill="x", padx=12, pady=(0, 10))

    live_event_scroll = ttk.Scrollbar(live_monitor_panel, orient="vertical", command=live_event_tree.yview)
    live_event_tree.configure(yscrollcommand=live_event_scroll.set)
    live_event_scroll.pack(side="right", fill="y", padx=(0, 12), pady=(0, 10))

    activity_tree = ttk.Treeview(activity_panel, columns=("timestamp", "user", "action", "summary"),
                                 show="headings", height=6, style="Admin.Treeview")
    activity_tree.heading("timestamp", text="TIME")
    activity_tree.heading("user", text="USER")
    activity_tree.heading("action", text="ACTION")
    activity_tree.heading("summary", text="DETAILS")
    activity_tree.column("timestamp", width=140, anchor="w")
    activity_tree.column("user", width=110, anchor="w")
    activity_tree.column("action", width=170, anchor="w")
    activity_tree.column("summary", width=420, anchor="w")
    activity_tree.pack(fill="x", padx=12, pady=(0, 10))

    activity_scroll = ttk.Scrollbar(activity_panel, orient="vertical", command=activity_tree.yview)
    activity_tree.configure(yscrollcommand=activity_scroll.set)
    activity_scroll.pack(side="right", fill="y", padx=(0, 12), pady=(0, 10))

    def _toggle_activity_panel():
        current = quick_actions["show_activity"]
        quick_actions["show_activity"] = toggle_panel_visibility(current)
        if current:
            activity_panel.pack_forget()
            activity_toggle.config(text="Show Recent Activity")
        else:
            activity_panel.pack(fill="x", padx=25, pady=(0, 12))
            activity_toggle.config(text="Hide Recent Activity")

    def _toggle_details_panel():
        current = quick_actions["show_details"]
        quick_actions["show_details"] = toggle_panel_visibility(current)
        if current:
            details_panel.pack_forget()
        else:
            details_panel.pack(fill="x", padx=25, pady=(0, 8))

    activity_toggle.config(command=_toggle_activity_panel)
    details_toggle.config(command=_toggle_details_panel)

    def _render_activity(rows):
        for item in activity_tree.get_children():
            activity_tree.delete(item)

        for row in rows:
            activity_tree.insert("", "end", values=(
                row["timestamp"], row["username"], row["action"], row["summary"]
            ))

    def _render_live_events(rows):
        for item in live_event_tree.get_children():
            live_event_tree.delete(item)

        for row in rows:
            formatted = format_live_event_row(row)
            live_event_tree.insert("", "end", values=(
                formatted["timestamp"], row.get("action") or "Activity", formatted["label"]
            ))

    def _load():
        """Refresh the operations view without rendering the old user table."""
        with get_connection() as conn:
            activity_rows = conn.execute(
                """SELECT timestamp, username, action, details
                   FROM logs ORDER BY id DESC LIMIT 12"""
            ).fetchall()

        activity_rows = [dict(r) for r in activity_rows]
        formatted_activity = format_activity_rows(activity_rows)
        _render_activity(filter_activity_logs(formatted_activity, ""))

        live_summary = summarize_live_events(activity_rows)
        live_summary_text.config(
            text=(
                f"Registrations: {live_summary['registrations']}   •   Logins: {live_summary['logins']}   •   "
                f"Latest: {live_summary['latest']}"
            )
        )
        _render_live_events(activity_rows[:8])

    # ── Workspace Action Menu ────────────────────────────────────────────────
    def _logout():
        log_activity("Logout", user_id=user_id, username=username)
        dash.destroy()
        from auth.login import login_window
        login_window()

    action_menu = tk.Menu(dash, tearoff=0, bg="#111827", fg="#F8FAFC", activebackground="#0EA5E9", activeforeground="white")
    action_menu.add_command(label="↻  Refresh Workspace", command=_load)
    action_menu.add_separator()
    for label, module_name in get_site_manager_actions():
        if module_name == "administration":
            continue
        action_menu.add_command(
            label=f"📁  Open {label}",
            command=lambda module_name=module_name: open_site_manager_module(dash, module_name),
        )
    action_menu.add_separator()
    action_menu.add_command(label="🚪  Log Out", command=_logout)

    def _logout():
        log_activity("Logout", user_id=user_id, username=username)
        dash.destroy()
        from auth.login import login_window
        login_window()

    action_menu = tk.Menu(dash, tearoff=0, bg="#111827", fg="#F8FAFC", activebackground="#0EA5E9", activeforeground="white")
    action_menu.add_command(label="↻  Refresh Workspace", command=_load)
    action_menu.add_separator()
    for label, module_name in get_site_manager_actions():
        if module_name == "administration":
            continue
        action_menu.add_command(
            label=f"📁  Open {label}",
            command=lambda module_name=module_name: open_site_manager_module(dash, module_name),
        )
    action_menu.add_separator()
    action_menu.add_command(label="🚪  Log Out", command=_logout)

    def _open_actions_menu(event=None):
        if event:
            action_menu.post(event.x_root, event.y_root)
        else:
            action_menu.post(dash.winfo_rootx() + dash.winfo_width() - 180, dash.winfo_rooty() + 60)

    action_btn.config(command=_open_actions_menu)

    _load()
    dash.mainloop()