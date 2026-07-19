"""
JEPA Site Manager — Operations Command Center (Redesigned)
A modern, responsive, dark-themed dashboard for construction operations.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import calendar

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


# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL THEME & COLORS
# ─────────────────────────────────────────────────────────────────────────────

# Extended color palette for the command center
COLORS = {
    "bg_main": "#0B1C2C",
    "bg_gradient": "#0F2A3F",
    "card_bg": "#132F4C",
    "sidebar_bg": "#0F1E2E",
    "header_bg": "#0B1C2C",
    "accent_blue": "#0EA5E9",
    "accent_orange": "#F59E0B",
    "accent_red": "#EF4444",
    "accent_green": "#22C55E",
    "accent_purple": "#A78BFA",
    "accent_teal": "#14B8A6",
    "text_white": "#F8FAFC",
    "text_muted": "#94A3B8",
    "border_subtle": "#1F3A4D",
    "success": "#10B981",
    "warning": "#F59E0B",
    "error": "#EF4444",
}


# ─────────────────────────────────────────────────────────────────────────────
# NAVIGATION STRUCTURE
# ─────────────────────────────────────────────────────────────────────────────

NAVIGATION_ITEMS = [
    ("🏠 Dashboard", "overview"),
    ("📋 Projects", "projects"),
    ("🏗️ Sites", "sites"),
    ("✓ Tasks", "tasks"),
    ("📊 Reports", "reports"),
    ("📦 Materials", "materials"),
    ("👥 Workforce", "workforce"),
    ("🔧 Equipment", "equipment"),
    ("⚠️ Issues", "issues"),
    ("📄 Documents", "documents"),
    ("✔️ Approvals", "approvals"),
    ("💰 BOQ", "boq"),
    ("📈 Analytics", "analytics"),
    ("🔔 Notifications", "notifications"),
]

OPERATIONS_ITEMS = [
    ("⚙️ Command Center", "command"),
    ("📅 My Calendar", "calendar"),
    ("⚡ Settings", "settings"),
]


# ─────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def _clear_frame(frame: tk.Widget, exclude: list[tk.Widget] | None = None) -> None:
    """Clear all widgets from a frame, optionally excluding some widgets.

    `exclude` should be a list of widget objects that will not be destroyed.
    """
    exclude = exclude or []
    for child in frame.winfo_children():
        if child in exclude:
            continue
        try:
            child.destroy()
        except Exception:
            # best-effort removal; ignore failures
            pass


def _create_card(parent: tk.Widget, bg_color: str = None) -> tk.Frame:
    """Create a styled card frame."""
    card = tk.Frame(
        parent,
        bg=bg_color or COLORS["card_bg"],
        highlightthickness=1,
        highlightbackground=COLORS["border_subtle"],
    )
    return card


def _show_toast(parent: tk.Misc, message: str, duration: int = 3000) -> None:
    """Show a toast notification."""
    toast = tk.Toplevel(parent)
    toast.wm_overrideredirect(True)
    toast.configure(bg=COLORS["accent_green"])
    
    label = tk.Label(
        toast,
        text=f"✓ {message}",
        fg=COLORS["text_white"],
        bg=COLORS["accent_green"],
        font=FONTS["body_bold"],
        padx=20,
        pady=12,
    )
    label.pack()
    
    x = parent.winfo_x() + parent.winfo_width() - 250
    y = parent.winfo_y() + parent.winfo_height() - 100
    toast.geometry(f"+{x}+{y}")
    
    toast.after(duration, toast.destroy)


def _get_live_time() -> str:
    """Get current time as string."""
    return datetime.now().strftime("%H:%M")


def _get_date_display() -> str:
    """Get current date as readable string."""
    return datetime.now().strftime("%d %b %Y")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN DASHBOARD REDESIGN
# ─────────────────────────────────────────────────────────────────────────────

def open_site_manager_hub(
    parent: tk.Misc | None = None,
    user_id: int | None = None,
    role: str | None = None,
) -> None:
    """Open the redesigned Operations Command Center dashboard."""
    
    role_label = normalize_role(role)
    role_name = get_role_title(role_label)
    accessible_actions = get_accessible_site_manager_actions(role_label)
    
    should_mainloop = parent is None
    if parent is None:
        window = tk.Tk()
    else:
        window = tk.Toplevel(parent)
    
    window.title("JEPA SITE MANAGER — Operations Command Center")
    window.geometry("1600x900")
    window.configure(bg=COLORS["bg_main"])
    
    # ─────── MAIN LAYOUT ───────
    window.grid_rowconfigure(1, weight=1)
    window.grid_columnconfigure(1, weight=1)
    
    # ═════════════════════════════════════════════════════════════════════════
    # 1. LEFT SIDEBAR
    # ═════════════════════════════════════════════════════════════════════════
    
    sidebar = tk.Frame(window, bg=COLORS["sidebar_bg"], width=280)
    sidebar.grid(row=0, column=0, rowspan=3, sticky="nsw", padx=0, pady=0)
    sidebar.grid_propagate(False)
    
    # Logo section
    logo_frame = tk.Frame(sidebar, bg=COLORS["sidebar_bg"])
    logo_frame.pack(fill="x", padx=16, pady=(16, 8))
    
    tk.Label(
        logo_frame,
        text="🏢 JEPA",
        fg=COLORS["accent_blue"],
        bg=COLORS["sidebar_bg"],
        font=("Segoe UI", 14, "bold"),
    ).pack(anchor="w")
    
    tk.Label(
        logo_frame,
        text="SITE MANAGER",
        fg=COLORS["text_white"],
        bg=COLORS["sidebar_bg"],
        font=("Segoe UI", 9, "bold"),
    ).pack(anchor="w")
    
    tk.Label(
        logo_frame,
        text="Operations Command Center",
        fg=COLORS["text_muted"],
        bg=COLORS["sidebar_bg"],
        font=FONTS["small"],
    ).pack(anchor="w", pady=(2, 0))
    
    # User section
    tk.Frame(sidebar, bg=COLORS["sidebar_bg"], height=1).pack(fill="x", padx=12, pady=(12, 8))
    
    user_frame = tk.Frame(sidebar, bg=COLORS["sidebar_bg"])
    user_frame.pack(fill="x", padx=12, pady=8)
    
    tk.Label(
        user_frame,
        text="👤 Admin User",
        fg=COLORS["text_white"],
        bg=COLORS["sidebar_bg"],
        font=FONTS["body_bold"],
    ).pack(anchor="w")
    
    status_frame = tk.Frame(user_frame, bg=COLORS["sidebar_bg"])
    status_frame.pack(anchor="w", pady=(4, 0))
    
    tk.Label(
        status_frame,
        text="● Online",
        fg=COLORS["accent_green"],
        bg=COLORS["sidebar_bg"],
        font=FONTS["small"],
    ).pack(side="left")
    
    tk.Label(
        status_frame,
        text=f"Role: {role_name}",
        fg=COLORS["text_muted"],
        bg=COLORS["sidebar_bg"],
        font=FONTS["small"],
    ).pack(side="left", padx=(12, 0))
    
    # Main navigation
    tk.Frame(sidebar, bg=COLORS["sidebar_bg"], height=1).pack(fill="x", padx=12, pady=(12, 8))
    
    tk.Label(
        sidebar,
        text="MAIN NAVIGATION",
        fg=COLORS["accent_orange"],
        bg=COLORS["sidebar_bg"],
        font=FONTS["label"],
    ).pack(anchor="w", padx=12, pady=(4, 8))
    
    nav_buttons = {}
    selected_action = tk.StringVar(value="overview")
    
    def _set_active(module_name: str) -> None:
        """Update active navigation button."""
        selected_action.set(module_name)
        for name, btn in nav_buttons.items():
            if name == module_name:
                btn.config(
                    bg=COLORS["accent_blue"],
                    fg=COLORS["text_white"],
                )
            else:
                btn.config(
                    bg=COLORS["sidebar_bg"],
                    fg=COLORS["text_muted"],
                )
        _render_content(module_name)
    
    def _on_nav_click(module_name: str):
        """Navigation button click handler."""
        _set_active(module_name)
    
    for label, module_name in NAVIGATION_ITEMS:
        btn = tk.Button(
            sidebar,
            text=label,
            command=lambda m=module_name: _on_nav_click(m),
            anchor="w",
            bg=COLORS["sidebar_bg"],
            fg=COLORS["text_muted"],
            activebackground=COLORS["accent_blue"],
            activeforeground=COLORS["text_white"],
            bd=0,
            relief="flat",
            padx=12,
            pady=10,
            font=FONTS["body"],
            cursor="hand2",
        )
        btn.pack(fill="x", padx=8, pady=2)
        nav_buttons[module_name] = btn
    
    # Operations section
    tk.Frame(sidebar, bg=COLORS["sidebar_bg"], height=1).pack(fill="x", padx=12, pady=(12, 8))
    
    tk.Label(
        sidebar,
        text="OPERATIONS",
        fg=COLORS["accent_purple"],
        bg=COLORS["sidebar_bg"],
        font=FONTS["label"],
    ).pack(anchor="w", padx=12, pady=(4, 8))
    
    for label, module_name in OPERATIONS_ITEMS:
        btn = tk.Button(
            sidebar,
            text=label,
            anchor="w",
            bg=COLORS["sidebar_bg"],
            fg=COLORS["text_muted"],
            activebackground=COLORS["accent_purple"],
            activeforeground=COLORS["text_white"],
            bd=0,
            relief="flat",
            padx=12,
            pady=10,
            font=FONTS["body"],
            cursor="hand2",
        )
        btn.pack(fill="x", padx=8, pady=2)
    
    # Spacer
    sidebar.grid_rowconfigure(1, weight=1)
    
    # Logout button
    tk.Frame(sidebar, bg=COLORS["sidebar_bg"], height=1).pack(fill="x", padx=12, pady=(12, 8))
    
    logout_btn = tk.Button(
        sidebar,
        text="🚪 Logout",
        command=window.quit,
        bg=COLORS["accent_red"],
        fg=COLORS["text_white"],
        activebackground="#DC2626",
        bd=0,
        relief="flat",
        padx=12,
        pady=10,
        font=FONTS["body_bold"],
        cursor="hand2",
    )
    logout_btn.pack(fill="x", padx=8, pady=(0, 12))
    
    # ═════════════════════════════════════════════════════════════════════════
    # 2. TOP HEADER BAR
    # ═════════════════════════════════════════════════════════════════════════
    
    header = tk.Frame(window, bg=COLORS["header_bg"], height=70, relief="flat")
    header.grid(row=0, column=1, sticky="ew", padx=0, pady=0)
    header.grid_propagate(False)
    
    # Left side - Greeting
    greeting_frame = tk.Frame(header, bg=COLORS["header_bg"])
    greeting_frame.pack(side="left", fill="both", expand=True, padx=20)
    
    tk.Label(
        greeting_frame,
        text=f"Good {('morning' if datetime.now().hour < 12 else 'afternoon' if datetime.now().hour < 18 else 'evening')}, Admin! 👋",
        fg=COLORS["text_white"],
        bg=COLORS["header_bg"],
        font=("Segoe UI", 14, "bold"),
    ).pack(anchor="w")
    
    tk.Label(
        greeting_frame,
        text="Here's what's happening across all projects and sites.",
        fg=COLORS["text_muted"],
        bg=COLORS["header_bg"],
        font=FONTS["small"],
    ).pack(anchor="w", pady=(2, 0))
    
    # Right side - Search, notifications, time
    control_frame = tk.Frame(header, bg=COLORS["header_bg"])
    control_frame.pack(side="right", fill="y", padx=20)
    
    # Search bar
    search_var = tk.StringVar()
    search_entry = tk.Entry(
        control_frame,
        textvariable=search_var,
        bg=COLORS["card_bg"],
        fg=COLORS["text_white"],
        insertbackground=COLORS["text_white"],
        bd=1,
        relief="solid",
        font=FONTS["small"],
    )
    search_entry.pack(side="left", padx=5)
    search_entry.insert(0, "🔍 Search anything...")
    
    def _on_search_focus(event):
        if search_entry.get() == "🔍 Search anything...":
            search_entry.delete(0, tk.END)
            search_entry.config(fg=COLORS["text_white"])
    
    def _on_search_blur(event):
        if search_entry.get() == "":
            search_entry.insert(0, "🔍 Search anything...")
            search_entry.config(fg=COLORS["text_muted"])
    
    search_entry.bind("<FocusIn>", _on_search_focus)
    search_entry.bind("<FocusOut>", _on_search_blur)
    
    # Notification bell
    def _show_notifications():
        messagebox.showinfo("Notifications", "You have 3 new notifications.")
    
    notif_btn = tk.Button(
        control_frame,
        text="🔔 (3)",
        command=_show_notifications,
        bg=COLORS["card_bg"],
        fg=COLORS["text_white"],
        activebackground=COLORS["accent_orange"],
        bd=0,
        relief="flat",
        font=FONTS["body"],
        cursor="hand2",
        padx=8,
        pady=4,
    )
    notif_btn.pack(side="left", padx=5)
    
    # Dark mode toggle (placeholder)
    tk.Button(
        control_frame,
        text="🌙",
        bg=COLORS["card_bg"],
        fg=COLORS["text_white"],
        activebackground=COLORS["accent_blue"],
        bd=0,
        relief="flat",
        font=FONTS["body"],
        cursor="hand2",
        padx=8,
        pady=4,
    ).pack(side="left", padx=5)
    
    # Date and time
    time_var = tk.StringVar(value=_get_live_time())
    time_label = tk.Label(
        control_frame,
        textvariable=time_var,
        fg=COLORS["accent_teal"],
        bg=COLORS["header_bg"],
        font=FONTS["body_bold"],
        padx=8,
    )
    time_label.pack(side="left", padx=5)
    
    def _update_time():
        time_var.set(_get_live_time())
        time_label.after(1000, _update_time)
    
    _update_time()
    
    # Date
    tk.Label(
        control_frame,
        text=_get_date_display(),
        fg=COLORS["text_muted"],
        bg=COLORS["header_bg"],
        font=FONTS["small"],
        padx=8,
    ).pack(side="left", padx=5)
    
    # Refresh button
    def _refresh_dashboard():
        _show_toast(window, "Dashboard refreshed")
        _render_content(selected_action.get())
    
    tk.Button(
        control_frame,
        text="🔄",
        command=_refresh_dashboard,
        bg=COLORS["card_bg"],
        fg=COLORS["accent_teal"],
        activebackground=COLORS["accent_teal"],
        activeforeground=COLORS["text_white"],
        bd=0,
        relief="flat",
        font=FONTS["body"],
        cursor="hand2",
        padx=8,
        pady=4,
    ).pack(side="left", padx=5)
    
    # Clear filters button
    tk.Button(
        control_frame,
        text="✕ Clear Filters",
        bg=COLORS["accent_orange"],
        fg=COLORS["text_white"],
        activebackground="#D97706",
        bd=0,
        relief="flat",
        font=FONTS["body"],
        cursor="hand2",
        padx=8,
        pady=4,
    ).pack(side="left", padx=5)
    
    # ═════════════════════════════════════════════════════════════════════════
    # 3. SUMMARY CARDS (TOP ROW)
    # ═════════════════════════════════════════════════════════════════════════
    
    summary_row = tk.Frame(window, bg=COLORS["bg_main"])
    summary_row.grid(row=1, column=1, sticky="ew", padx=20, pady=12)
    
    def _create_summary_card(
        parent: tk.Widget,
        icon: str,
        value: str,
        label: str,
        subtitle: str,
        color: str,
    ) -> None:
        """Create a summary card."""
        card = _create_card(parent)
        card.pack(side="left", fill="both", expand=True, padx=4)
        
        # Icon and value
        top_frame = tk.Frame(card, bg=COLORS["card_bg"])
        top_frame.pack(fill="x", padx=12, pady=(12, 0))
        
        tk.Label(
            top_frame,
            text=icon,
            fg=color,
            bg=COLORS["card_bg"],
            font=("Segoe UI", 20),
        ).pack(side="left")
        
        tk.Label(
            top_frame,
            text=value,
            fg=COLORS["text_white"],
            bg=COLORS["card_bg"],
            font=("Segoe UI", 16, "bold"),
            padx=8,
        ).pack(side="left")
        
        # Label and subtitle
        tk.Label(
            card,
            text=label,
            fg=color,
            bg=COLORS["card_bg"],
            font=FONTS["label"],
        ).pack(anchor="w", padx=12, pady=(8, 0))
        
        tk.Label(
            card,
            text=subtitle,
            fg=COLORS["text_muted"],
            bg=COLORS["card_bg"],
            font=FONTS["small"],
        ).pack(anchor="w", padx=12, pady=(0, 12))
    
    metrics_data = get_admin_dashboard_metrics()
    projects = list_projects()
    
    _create_summary_card(
        summary_row,
        "🏗️",
        str(metrics_data.get("active_projects", 0)),
        "Active Sites",
        "Live construction locations",
        COLORS["accent_blue"],
    )
    
    _create_summary_card(
        summary_row,
        "📋",
        str(metrics_data.get("active_projects", 0)),
        "Active Projects",
        "Projects in progress",
        COLORS["accent_orange"],
    )
    
    _create_summary_card(
        summary_row,
        "📄",
        str(metrics_data.get("missing_reports", 0)),
        "Missing Reports",
        "Reports overdue today",
        COLORS["accent_red"],
    )
    
    _create_summary_card(
        summary_row,
        "✔️",
        "2",
        "Pending Approvals",
        "Awaiting review",
        COLORS["accent_purple"],
    )
    
    _create_summary_card(
        summary_row,
        "📦",
        str(len(metrics_data.get("low_stock_alerts", []))),
        "Material Alerts",
        "Low-stock items",
        COLORS["accent_green"],
    )
    
    _create_summary_card(
        summary_row,
        "📈",
        "87%",
        "Overall Progress",
        "System-wide completion",
        COLORS["accent_teal"],
    )
    
    # ═════════════════════════════════════════════════════════════════════════
    # 4. MAIN CONTENT AREA
    # ═════════════════════════════════════════════════════════════════════════
    
    content_frame = tk.Frame(window, bg=COLORS["bg_main"])
    content_frame.grid(row=2, column=1, sticky="nsew", padx=20, pady=12)
    content_frame.grid_rowconfigure(0, weight=1)
    content_frame.grid_columnconfigure(0, weight=1)
    
    content_frame.grid_rowconfigure(0, weight=1)
    content_frame.grid_columnconfigure(1, weight=1)
    
    # ─────── QUICK ACTION BUTTONS ───────
    actions_frame = tk.Frame(content_frame, bg=COLORS["bg_main"])
    actions_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
    
    def _create_action_button(parent, text, cmd, color):
        """Create an action button."""
        btn = tk.Button(
            parent,
            text=text,
            command=cmd,
            bg=color,
            fg=COLORS["text_white"],
            activebackground=color,
            bd=0,
            relief="flat",
            padx=16,
            pady=10,
            font=FONTS["body_bold"],
            cursor="hand2",
        )
        btn.pack(side="left", padx=6)
        return btn
    
    def _new_project():
        _show_toast(window, "Opening New Project form")
        open_site_manager_module(window, "projects", user_id=user_id, role=role_label)
    
    def _add_site():
        _show_toast(window, "Opening Add Site form")
        open_site_manager_module(window, "projects", user_id=user_id, role=role_label)
    
    def _create_report():
        _show_toast(window, "Creating new report")
        open_site_manager_module(window, "reports", user_id=user_id, role=role_label)
    
    def _material_request():
        _show_toast(window, "Opening Material Request form")
        open_site_manager_module(window, "materials", user_id=user_id, role=role_label)
    
    def _add_task():
        _show_toast(window, "Opening Add Task form")
        open_site_manager_module(window, "tasks", user_id=user_id, role=role_label)
    
    def _mark_attendance():
        _show_toast(window, "Opening Attendance form")
        open_site_manager_module(window, "workforce", user_id=user_id, role=role_label)
    
    _create_action_button(actions_frame, "➕ New Project", _new_project, COLORS["accent_blue"])
    _create_action_button(actions_frame, "➕ Add Site", _add_site, COLORS["accent_green"])
    _create_action_button(actions_frame, "📊 Create Report", _create_report, COLORS["accent_orange"])
    _create_action_button(actions_frame, "📦 Material Request", _material_request, COLORS["accent_purple"])
    _create_action_button(actions_frame, "✓ Add Task", _add_task, COLORS["accent_teal"])
    _create_action_button(actions_frame, "👥 Attendance", _mark_attendance, COLORS["accent_blue"])
    
    # ─────── CONTENT SECTIONS (Alerts / Progress / Calendar / Activity) ───────
    # Create a persistent sections frame below the quick actions where the
    # 2x2 grid of panels will live. This keeps quick actions stable while
    # allowing overview to populate these panels.
    sections_frame = tk.Frame(content_frame, bg=COLORS["bg_main"])
    sections_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(6, 0))
    sections_frame.grid_columnconfigure(0, weight=1)
    sections_frame.grid_columnconfigure(1, weight=1)

    def render_alerts(parent: tk.Widget) -> None:
        """Render Alerts panel into the provided parent widget."""
        _clear_frame(parent)
        card = _create_card(parent)
        card.pack(fill="both", expand=True, padx=6, pady=6)

        tk.Label(
            card,
            text="🚨 Alerts & Watchlist",
            fg=COLORS["accent_red"],
            bg=COLORS["card_bg"],
            font=FONTS["h3"],
        ).pack(anchor="w", padx=12, pady=(12, 4))

        sample_alerts = [
            ("Missing Reports", "2 reports overdue", COLORS["accent_red"], "Today"),
            ("Low Stock", "5 items", COLORS["accent_orange"], "1h ago"),
            ("Equipment Fault", "1 critical", COLORS["accent_red"], "Now"),
        ]

        for title, value, color, time in sample_alerts:
            row = tk.Frame(card, bg=COLORS["card_bg"]) 
            row.pack(fill="x", padx=12, pady=6)

            tk.Label(row, text=title, fg=color, bg=COLORS["card_bg"], font=FONTS["body_bold"]).pack(side="left", anchor="w")
            tk.Label(row, text=value, fg=COLORS["text_muted"], bg=COLORS["card_bg"], font=FONTS["small"]).pack(side="left", padx=12)
            tk.Label(row, text=time, fg=COLORS["text_muted"], bg=COLORS["card_bg"], font=FONTS["small"]).pack(side="right")

    def render_project_progress(parent: tk.Widget) -> None:
        """Render a compact project progress panel."""
        _clear_frame(parent)
        card = _create_card(parent)
        card.pack(fill="both", expand=True, padx=6, pady=6)

        tk.Label(
            card,
            text="📊 Project Progress",
            fg=COLORS["accent_teal"],
            bg=COLORS["card_bg"],
            font=FONTS["h3"],
        ).pack(anchor="w", padx=12, pady=(12, 4))

        projects_sample = list_projects()[:4]
        if not projects_sample:
            projects_sample = [{"project_name": "Sample Project A", "progress_percent": 45, "status": "Active"},
                               {"project_name": "Sample Project B", "progress_percent": 78, "status": "On Track"}]

        for project in projects_sample:
            item = tk.Frame(card, bg=COLORS["card_bg"])
            item.pack(fill="x", padx=12, pady=6)

            tk.Label(item, text=project.get("project_name", "Unnamed"), fg=COLORS["text_white"], bg=COLORS["card_bg"], font=FONTS["body_bold"]).pack(anchor="w")
            pct = int(project.get("progress_percent", 0))
            progress_color = COLORS["accent_green"] if pct >= 75 else COLORS["accent_orange"] if pct >= 50 else COLORS["accent_red"]

            bar = tk.Frame(item, bg=COLORS["bg_main"], height=8)
            bar.pack(fill="x", pady=6)
            filled = tk.Frame(bar, bg=progress_color, height=8)
            filled.place(relwidth=max(pct / 100, 0.01), relheight=1)

            tk.Label(item, text=f"{pct}% • {project.get('status', 'Unknown')}", fg=COLORS["text_muted"], bg=COLORS["card_bg"], font=FONTS["small"]).pack(anchor="w")

    def render_calendar(parent: tk.Widget) -> None:
        """Render a mini calendar widget."""
        _clear_frame(parent)
        card = _create_card(parent)
        card.pack(fill="both", expand=True, padx=6, pady=6)

        tk.Label(card, text="📅 Calendar", fg=COLORS["accent_purple"], bg=COLORS["card_bg"], font=FONTS["h3"]).pack(anchor="w", padx=12, pady=(12, 4))

        today = datetime.now()
        cal_text = f"{today.strftime('%B %Y')}\n"
        cal_text += "Mo Tu We Th Fr Sa Su\n"
        cal = calendar.monthcalendar(today.year, today.month)
        for week in cal:
            for day in week:
                if day == 0:
                    cal_text += "   "
                elif day == today.day:
                    cal_text += f"[{day:2d}]"
                else:
                    cal_text += f"{day:3d} "
            cal_text += "\n"

        tk.Label(card, text=cal_text, fg=COLORS["text_muted"], bg=COLORS["card_bg"], font=("Courier", 9), justify="left").pack(anchor="w", padx=12, pady=(0, 12))

    def render_activity_feed(parent: tk.Widget) -> None:
        """Render a recent activity feed (scrollable)."""
        _clear_frame(parent)
        card = _create_card(parent)
        card.pack(fill="both", expand=True, padx=6, pady=6)

        tk.Label(card, text="🕘 Recent Activity", fg=COLORS["accent_blue"], bg=COLORS["card_bg"], font=FONTS["h3"]).pack(anchor="w", padx=12, pady=(12, 4))

        feed_frame = tk.Frame(card, bg=COLORS["card_bg"])
        feed_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # Sample activity items
        sample_feed = [
            ("12:02", "Report submitted - Site A"),
            ("11:47", "Worker checked in - Site B"),
            ("10:30", "Material requested - Cement"),
            ("09:15", "Equipment fault reported - Crane 3"),
        ]

        for tstamp, text in sample_feed:
            row = tk.Frame(feed_frame, bg=COLORS["card_bg"])
            row.pack(fill="x", pady=6)
            tk.Label(row, text=tstamp, fg=COLORS["text_muted"], bg=COLORS["card_bg"], font=FONTS["small"]).pack(side="left")
            tk.Label(row, text=text, fg=COLORS["text_white"], bg=COLORS["card_bg"], font=FONTS["body"]).pack(side="left", padx=8)

    # Arrange the 2x2 grid inside sections_frame using grid (persistent)
    sections_frame.grid_rowconfigure(0, weight=1)
    sections_frame.grid_rowconfigure(1, weight=1)
    sections_frame.grid_columnconfigure(0, weight=1)
    sections_frame.grid_columnconfigure(1, weight=1)

    panel_alerts = tk.Frame(sections_frame, bg=COLORS["bg_main"])
    panel_progress = tk.Frame(sections_frame, bg=COLORS["bg_main"])
    panel_calendar = tk.Frame(sections_frame, bg=COLORS["bg_main"])
    panel_activity = tk.Frame(sections_frame, bg=COLORS["bg_main"])

    panel_alerts.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
    panel_progress.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
    panel_calendar.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)
    panel_activity.grid(row=1, column=1, sticky="nsew", padx=6, pady=6)

    # Initial render of the 4 panels (called once and persistent)
    render_alerts(panel_alerts)
    render_project_progress(panel_progress)
    render_calendar(panel_calendar)
    render_activity_feed(panel_activity)

    # Main area for module-specific content (placed below sections)
    main_area = tk.Frame(content_frame, bg=COLORS["bg_main"])
    main_area.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=0, pady=(6, 0))
    main_area.grid_rowconfigure(0, weight=1)
    main_area.grid_columnconfigure(0, weight=1)
    main_area.grid_columnconfigure(1, weight=1)

    # ─────── MAIN CONTENT RENDERERS ───────
    
    def _render_overview() -> None:
        """Render dashboard overview into `main_area`."""
        _clear_frame(main_area)

        main_area.grid_rowconfigure(0, weight=1)
        main_area.grid_columnconfigure(1, weight=1)

        # Left panel - Daily Operations Brief
        left_panel = _create_card(main_area)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        
        tk.Label(
            left_panel,
            text="📋 Daily Operations Brief",
            fg=COLORS["accent_blue"],
            bg=COLORS["card_bg"],
            font=FONTS["h3"],
        ).pack(anchor="w", padx=12, pady=(12, 4))
        
        tk.Label(
            left_panel,
            text="Real-time project and site status",
            fg=COLORS["text_muted"],
            bg=COLORS["card_bg"],
            font=FONTS["small"],
        ).pack(anchor="w", padx=12, pady=(0, 12))
        
        # Summary boxes
        summary_boxes = [
            ("Executive Summary", f"{metrics_data.get('active_projects', 0)} active projects", COLORS["accent_blue"]),
            ("Project Health", f"{metrics_data.get('delayed_projects', 0)} delayed", COLORS["accent_orange"]),
            ("Site Readiness", f"{metrics_data.get('equipment_issues', 0)} issues", COLORS["accent_green"]),
        ]
        
        for title, content, color in summary_boxes:
            box = tk.Frame(left_panel, bg=COLORS["bg_main"], highlightthickness=2, highlightbackground=color)
            box.pack(fill="x", padx=12, pady=4)
            
            tk.Label(
                box,
                text=title,
                fg=color,
                bg=COLORS["bg_main"],
                font=FONTS["label"],
            ).pack(anchor="w", padx=8, pady=(4, 0))
            
            tk.Label(
                box,
                text=content,
                fg=COLORS["text_white"],
                bg=COLORS["bg_main"],
                font=FONTS["body_bold"],
            ).pack(anchor="w", padx=8, pady=(0, 4))
        
        # Crew and tasks info
        info_items = [
            ("👥 Crew on Site", f"{metrics_data.get('workforce_on_site', 0)} workers"),
            ("✓ Tasks Due Today", "8 tasks"),
            ("⚠️ Issues Open", f"{metrics_data.get('equipment_issues', 0)} open"),
            ("🔧 Equipment in Use", "12 units"),
        ]
        
        for icon, value in info_items:
            item_frame = tk.Frame(left_panel, bg=COLORS["card_bg"])
            item_frame.pack(fill="x", padx=12, pady=4)
            
            tk.Label(
                item_frame,
                text=icon,
                fg=COLORS["accent_teal"],
                bg=COLORS["card_bg"],
                font=FONTS["body"],
            ).pack(side="left", padx=4)
            
            tk.Label(
                item_frame,
                text=value,
                fg=COLORS["text_white"],
                bg=COLORS["card_bg"],
                font=FONTS["body_bold"],
            ).pack(side="left", padx=4)
        
        # Right panel - Overview insights (do NOT recreate persistent panels)
        right_panel = tk.Frame(main_area, bg=COLORS["bg_main"])
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        right_panel.grid_rowconfigure(0, weight=1)
        
        insights_card = _create_card(right_panel)
        insights_card.pack(fill="both", expand=True, padx=0, pady=0)
        
        tk.Label(
            insights_card,
            text="🔎 Overview Insights",
            fg=COLORS["accent_blue"],
            bg=COLORS["card_bg"],
            font=FONTS["h3"],
        ).pack(anchor="w", padx=12, pady=(12, 4))
        
        tk.Label(
            insights_card,
            text="Key highlights and recent summary for operators.",
            fg=COLORS["text_muted"],
            bg=COLORS["card_bg"],
            font=FONTS["small"],
        ).pack(anchor="w", padx=12, pady=(0, 12))
        
        for k, v in [
            ("Active Projects", metrics_data.get("active_projects", 0)),
            ("Workers On Site", metrics_data.get("workforce_on_site", 0)),
            ("Equipment Issues", metrics_data.get("equipment_issues", 0)),
        ]:
            row = tk.Frame(insights_card, bg=COLORS["card_bg"])
            row.pack(fill="x", padx=12, pady=6)
            tk.Label(row, text=k, fg=COLORS["text_muted"], bg=COLORS["card_bg"], font=FONTS["small"]).pack(side="left")
            tk.Label(row, text=str(v), fg=COLORS["text_white"], bg=COLORS["card_bg"], font=FONTS["body_bold"]).pack(side="right")
    
    def _render_projects() -> None:
        """Render projects view into `main_area`."""
        _clear_frame(main_area)

        tk.Label(
            main_area,
            text="📋 Projects Workspace",
            fg=COLORS["accent_blue"],
            bg=COLORS["bg_main"],
            font=FONTS["h2"],
        ).pack(anchor="w", padx=0, pady=(12, 4))

        tk.Label(
            main_area,
            text="Browse and manage all active projects",
            fg=COLORS["text_muted"],
            bg=COLORS["bg_main"],
            font=FONTS["small"],
        ).pack(anchor="w", padx=0, pady=(0, 12))

        tk.Button(
            main_area,
            text="📂 Open Full Projects Module",
            command=lambda: open_site_manager_module(window, "projects", user_id=user_id, role=role_label),
            bg=COLORS["accent_blue"],
            fg=COLORS["text_white"],
            activebackground=COLORS["accent_blue"],
            bd=0,
            relief="flat",
            padx=16,
            pady=10,
            font=FONTS["body_bold"],
            cursor="hand2",
        ).pack(anchor="w", padx=0)
    
    def _render_reports() -> None:
        """Render reports view into `main_area`."""
        _clear_frame(main_area)

        tk.Label(
            main_area,
            text="📊 Reports Workspace",
            fg=COLORS["accent_orange"],
            bg=COLORS["bg_main"],
            font=FONTS["h2"],
        ).pack(anchor="w", padx=0, pady=(12, 4))

        tk.Label(
            main_area,
            text="Create, review, and manage site reports",
            fg=COLORS["text_muted"],
            bg=COLORS["bg_main"],
            font=FONTS["small"],
        ).pack(anchor="w", padx=0, pady=(0, 12))

        tk.Button(
            main_area,
            text="📄 Open Full Reports Module",
            command=lambda: open_site_manager_module(window, "reports", user_id=user_id, role=role_label),
            bg=COLORS["accent_orange"],
            fg=COLORS["text_white"],
            activebackground=COLORS["accent_orange"],
            bd=0,
            relief="flat",
            padx=16,
            pady=10,
            font=FONTS["body_bold"],
            cursor="hand2",
        ).pack(anchor="w", padx=0)
    
    def _render_materials() -> None:
        """Render materials view into `main_area`."""
        _clear_frame(main_area)

        tk.Label(
            main_area,
            text="📦 Materials Workspace",
            fg=COLORS["accent_purple"],
            bg=COLORS["bg_main"],
            font=FONTS["h2"],
        ).pack(anchor="w", padx=0, pady=(12, 4))

        tk.Label(
            main_area,
            text="Track inventory and material requests",
            fg=COLORS["text_muted"],
            bg=COLORS["bg_main"],
            font=FONTS["small"],
        ).pack(anchor="w", padx=0, pady=(0, 12))

        tk.Button(
            main_area,
            text="📦 Open Full Materials Module",
            command=lambda: open_site_manager_module(window, "materials", user_id=user_id, role=role_label),
            bg=COLORS["accent_purple"],
            fg=COLORS["text_white"],
            activebackground=COLORS["accent_purple"],
            bd=0,
            relief="flat",
            padx=16,
            pady=10,
            font=FONTS["body_bold"],
            cursor="hand2",
        ).pack(anchor="w", padx=0)
    
    def _render_workforce() -> None:
        """Render workforce view into `main_area`."""
        _clear_frame(main_area)

        tk.Label(
            main_area,
            text="👥 Workforce Workspace",
            fg=COLORS["accent_teal"],
            bg=COLORS["bg_main"],
            font=FONTS["h2"],
        ).pack(anchor="w", padx=0, pady=(12, 4))

        tk.Label(
            main_area,
            text="Manage attendance and workforce deployment",
            fg=COLORS["text_muted"],
            bg=COLORS["bg_main"],
            font=FONTS["small"],
        ).pack(anchor="w", padx=0, pady=(0, 12))

        tk.Button(
            main_area,
            text="👥 Open Full Workforce Module",
            command=lambda: open_site_manager_module(window, "workforce", user_id=user_id, role=role_label),
            bg=COLORS["accent_teal"],
            fg=COLORS["text_white"],
            activebackground=COLORS["accent_teal"],
            bd=0,
            relief="flat",
            padx=16,
            pady=10,
            font=FONTS["body_bold"],
            cursor="hand2",
        ).pack(anchor="w", padx=0)
    
    def _render_content(module_name: str) -> None:
        """Route content rendering based on module."""

        def _render_generic_module(name: str) -> None:
            """Render a simple landing page for modules without a dedicated renderer."""
            _clear_frame(main_area)
            title = (name or "Module").replace("_", " ").title()

            tk.Label(
                main_area,
                text=f"📁 {title} Workspace",
                fg=COLORS["accent_blue"],
                bg=COLORS["bg_main"],
                font=FONTS["h2"],
            ).pack(anchor="w", padx=0, pady=(12, 4))

            tk.Label(
                main_area,
                text=f"This is the {title} landing page. Use the button below to open the full module.",
                fg=COLORS["text_muted"],
                bg=COLORS["bg_main"],
                font=FONTS["small"],
            ).pack(anchor="w", padx=0, pady=(0, 12))

            tk.Button(
                main_area,
                text=f"Open Full {title} Module",
                command=lambda: open_site_manager_module(window, name, user_id=user_id, role=role_label),
                bg=COLORS["accent_blue"],
                fg=COLORS["text_white"],
                activebackground=COLORS["accent_blue"],
                bd=0,
                relief="flat",
                padx=16,
                pady=10,
                font=FONTS["body_bold"],
                cursor="hand2",
            ).pack(anchor="w", padx=0)

        full_window_modules = {"projects", "reports", "materials", "workforce", "equipment", "tasks"}
        if module_name in full_window_modules:
            _clear_frame(main_area)
            tk.Label(
                main_area,
                text=f"Opening {module_name.replace('_', ' ').title()} module...",
                fg=COLORS["accent_blue"],
                bg=COLORS["bg_main"],
                font=FONTS["h2"],
            ).pack(anchor="w", padx=0, pady=(12, 4))
            tk.Label(
                main_area,
                text="The full module window has been opened. Continue working in the new window.",
                fg=COLORS["text_muted"],
                bg=COLORS["bg_main"],
                font=FONTS["small"],
            ).pack(anchor="w", padx=0, pady=(0, 12))
            open_site_manager_module(window, module_name, user_id=user_id, role=role_label)
            return

        renderers = {
            "overview": _render_overview,
            "projects": _render_projects,
            "reports": _render_reports,
            "materials": _render_materials,
            "workforce": _render_workforce,
        }

        if module_name in renderers:
            renderers[module_name]()
        else:
            _render_generic_module(module_name)
    
    # ═════════════════════════════════════════════════════════════════════════
    # 5. FOOTER SUMMARY BAR
    # ═════════════════════════════════════════════════════════════════════════
    
    footer = _create_card(window)
    footer.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20, pady=12)
    
    footer_content = tk.Frame(footer, bg=COLORS["card_bg"])
    footer_content.pack(fill="x", padx=12, pady=10)
    
    # Footer stats
    footer_stats = [
        ("Total Projects", str(len(projects))),
        ("Active Sites", str(metrics_data.get("active_projects", 0))),
        ("Total Users", "24"),
        ("Total Tasks", "156"),
        ("Completion Rate", "87%"),
        ("System Status", "🟢 Operational"),
    ]
    
    for label, value in footer_stats:
        stat_frame = tk.Frame(footer_content, bg=COLORS["card_bg"])
        stat_frame.pack(side="left", fill="x", expand=True, padx=12)
        
        tk.Label(
            stat_frame,
            text=label,
            fg=COLORS["text_muted"],
            bg=COLORS["card_bg"],
            font=FONTS["small"],
        ).pack(anchor="w")
        
        tk.Label(
            stat_frame,
            text=value,
            fg=COLORS["text_white"],
            bg=COLORS["card_bg"],
            font=FONTS["body_bold"],
        ).pack(anchor="w")
    
    # ═════════════════════════════════════════════════════════════════════════
    # 6. INITIALIZE
    # ═════════════════════════════════════════════════════════════════════════
    
    _set_active("overview")
    
    if should_mainloop:
        window.mainloop()
