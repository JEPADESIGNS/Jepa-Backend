"""Morning Operations Center - Role-specific operational dashboard after login.

This becomes the default landing page for all authenticated users.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import threading

from ui.themes import FONTS, get_theme
from database.db import get_connection
from jepa_site_manager.core.dashboard_service import (
    get_active_projects_count,
    get_missing_reports_count,
    get_low_stock_alerts,
    get_project_summary,
    get_recent_activity,
)
from jepa_site_manager.core.operations_service import (
    get_today_priorities,
    get_role_specific_alerts,
    get_quick_actions,
    get_user_dashboard_greeting,
)
from dashboard import (
    normalize_role,
    get_role_title,
    open_site_manager_module,
)
from utils.session import session


# ─────────────────────────────────────────────────────────────────────────────
# COLOR SCHEME
# ─────────────────────────────────────────────────────────────────────────────

COLORS = {
    "bg_main": "#0B1C2C",
    "bg_secondary": "#0F2A3F",
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
    "critical": "#DC2626",
    "warning": "#F59E0B",
    "info": "#0EA5E9",
    "success": "#10B981",
}


def _create_card(parent: tk.Widget, bg_color: str = None) -> tk.Frame:
    """Create a styled card frame."""
    card = tk.Frame(
        parent,
        bg=bg_color or COLORS["card_bg"],
        highlightthickness=1,
        highlightbackground=COLORS["border_subtle"],
    )
    return card


def _clear_frame(frame: tk.Widget) -> None:
    """Clear all widgets from a frame."""
    for child in frame.winfo_children():
        try:
            child.destroy()
        except Exception:
            pass


def open_morning_operations_center(
    parent: tk.Misc | None = None,
    user_id: int | None = None,
    username: str | None = None,
    role: str | None = None,
) -> None:
    """Open the Morning Operations Center - role-specific operational dashboard."""
    
    role_label = normalize_role(role)
    role_name = get_role_title(role_label)
    
    should_mainloop = parent is None
    if parent is None:
        window = tk.Tk()
    else:
        window = tk.Toplevel(parent)
    
    window.title("JEPA Site Manager — Morning Operations Center")
    window.geometry("1400x900")
    window.configure(bg=COLORS["bg_main"])
    
    # ─────── MAIN LAYOUT ───────
    window.grid_rowconfigure(1, weight=1)
    window.grid_columnconfigure(1, weight=1)
    
    # ═════════════════════════════════════════════════════════════════════════
    # 1. HEADER
    # ═════════════════════════════════════════════════════════════════════════
    
    header = tk.Frame(window, bg=COLORS["header_bg"], height=100, relief="flat")
    header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
    header.grid_propagate(False)
    
    # Left side - Greeting
    greeting_frame = tk.Frame(header, bg=COLORS["header_bg"])
    greeting_frame.pack(side="left", fill="both", expand=True, padx=20, pady=12)
    
    greeting_text = get_user_dashboard_greeting(role_label, username or "User")
    tk.Label(
        greeting_frame,
        text=greeting_text,
        fg=COLORS["text_white"],
        bg=COLORS["header_bg"],
        font=("Segoe UI", 14, "bold"),
    ).pack(anchor="w")
    
    # Date and user info
    info_text = f"📅 {datetime.now().strftime('%A, %d %B %Y')} • Role: {role_name}"
    tk.Label(
        greeting_frame,
        text=info_text,
        fg=COLORS["text_muted"],
        bg=COLORS["header_bg"],
        font=FONTS["small"],
    ).pack(anchor="w", pady=(2, 0))
    
    # Right side - Controls
    control_frame = tk.Frame(header, bg=COLORS["header_bg"])
    control_frame.pack(side="right", fill="y", padx=20, pady=12)
    
    # Time display
    time_var = tk.StringVar(value=datetime.now().strftime("%H:%M"))
    time_label = tk.Label(
        control_frame,
        textvariable=time_var,
        fg=COLORS["accent_teal"],
        bg=COLORS["header_bg"],
        font=("Segoe UI", 16, "bold"),
        padx=8,
    )
    time_label.pack(side="left", padx=5)
    
    def _update_time():
        time_var.set(datetime.now().strftime("%H:%M"))
        time_label.after(1000, _update_time)
    
    _update_time()
    
    # Refresh button
    def _refresh_dashboard():
        _clear_frame(main_content)
        _render_main_content()
    
    tk.Button(
        control_frame,
        text="🔄 Refresh",
        command=_refresh_dashboard,
        bg=COLORS["accent_teal"],
        fg=COLORS["text_white"],
        bd=0,
        relief="flat",
        padx=12,
        pady=6,
        font=FONTS["body_bold"],
        cursor="hand2",
    ).pack(side="left", padx=5)
    
    # Open Full Hub button
    def _open_full_hub():
        from jepa_site_manager.core.hub import open_site_manager_hub
        open_site_manager_hub(window, user_id=user_id, role=role_label)
    
    tk.Button(
        control_frame,
        text="→ Full Dashboard",
        command=_open_full_hub,
        bg=COLORS["accent_blue"],
        fg=COLORS["text_white"],
        bd=0,
        relief="flat",
        padx=12,
        pady=6,
        font=FONTS["body"],
        cursor="hand2",
    ).pack(side="left", padx=5)
    
    # ═════════════════════════════════════════════════════════════════════════
    # 2. MAIN CONTENT
    # ═════════════════════════════════════════════════════════════════════════
    
    main_content = tk.Frame(window, bg=COLORS["bg_main"])
    main_content.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=20, pady=20)
    main_content.grid_rowconfigure(0, weight=1)
    main_content.grid_columnconfigure(0, weight=1)
    
    def _render_main_content():
        """Render the role-specific dashboard content."""
        # Create a scrollable canvas for long content
        canvas = tk.Canvas(main_content, bg=COLORS["bg_main"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_content, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS["bg_main"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # ─────── TOP ROW: SUMMARY CARDS ───────
        summary_row = tk.Frame(scrollable_frame, bg=COLORS["bg_main"])
        summary_row.pack(fill="x", pady=(0, 12))
        
        # Active Projects
        card1 = _create_card(summary_row)
        card1.pack(side="left", fill="both", expand=True, padx=(0, 8))
        
        active_count = get_active_projects_count()
        tk.Label(card1, text="📁", fg=COLORS["accent_blue"], bg=COLORS["card_bg"], font=("Segoe UI", 20)).pack(anchor="w", padx=12, pady=(12, 0))
        tk.Label(card1, text=str(active_count), fg=COLORS["accent_blue"], bg=COLORS["card_bg"], font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=12, pady=(0, 2))
        tk.Label(card1, text="Active Projects", fg=COLORS["text_muted"], bg=COLORS["card_bg"], font=FONTS["small"]).pack(anchor="w", padx=12, pady=(0, 12))
        
        # Missing Reports
        card2 = _create_card(summary_row)
        card2.pack(side="left", fill="both", expand=True, padx=8)
        
        missing_count = get_missing_reports_count()
        tk.Label(card2, text="📋", fg=COLORS["accent_orange"], bg=COLORS["card_bg"], font=("Segoe UI", 20)).pack(anchor="w", padx=12, pady=(12, 0))
        tk.Label(card2, text=str(missing_count), fg=COLORS["accent_orange"], bg=COLORS["card_bg"], font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=12, pady=(0, 2))
        tk.Label(card2, text="Reports Due", fg=COLORS["text_muted"], bg=COLORS["card_bg"], font=FONTS["small"]).pack(anchor="w", padx=12, pady=(0, 12))
        
        # Low Stock Alerts
        card3 = _create_card(summary_row)
        card3.pack(side="left", fill="both", expand=True, padx=8)
        
        low_stock = len(get_low_stock_alerts())
        tk.Label(card3, text="📦", fg=COLORS["accent_red"], bg=COLORS["card_bg"], font=("Segoe UI", 20)).pack(anchor="w", padx=12, pady=(12, 0))
        tk.Label(card3, text=str(low_stock), fg=COLORS["accent_red"], bg=COLORS["card_bg"], font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=12, pady=(0, 2))
        tk.Label(card3, text="Stock Alerts", fg=COLORS["text_muted"], bg=COLORS["card_bg"], font=FONTS["small"]).pack(anchor="w", padx=12, pady=(0, 12))
        
        # Pending Approvals
        card4 = _create_card(summary_row)
        card4.pack(side="left", fill="both", expand=True, padx=(8, 0))
        
        tk.Label(card4, text="✓", fg=COLORS["accent_green"], bg=COLORS["card_bg"], font=("Segoe UI", 20)).pack(anchor="w", padx=12, pady=(12, 0))
        tk.Label(card4, text="2", fg=COLORS["accent_green"], bg=COLORS["card_bg"], font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=12, pady=(0, 2))
        tk.Label(card4, text="Pending Approvals", fg=COLORS["text_muted"], bg=COLORS["card_bg"], font=FONTS["small"]).pack(anchor="w", padx=12, pady=(0, 12))
        
        # ─────── MIDDLE ROW: Priorities + Alerts + Quick Actions ───────
        middle_row = tk.Frame(scrollable_frame, bg=COLORS["bg_main"])
        middle_row.pack(fill="both", expand=True, pady=(0, 12))
        middle_row.grid_columnconfigure(0, weight=2)
        middle_row.grid_columnconfigure(1, weight=1)
        middle_row.grid_columnconfigure(2, weight=1)
        
        # Left: Today's Priorities
        priority_card = _create_card(middle_row)
        priority_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)
        
        tk.Label(priority_card, text="⚡ Today's Priorities", fg=COLORS["accent_orange"], bg=COLORS["card_bg"], font=FONTS["h3"]).pack(anchor="w", padx=12, pady=(12, 8))
        
        priorities = get_today_priorities(user_id, role_label)
        if priorities:
            for i, priority in enumerate(priorities[:5]):
                item_frame = tk.Frame(priority_card, bg=COLORS["bg_secondary"], highlightthickness=1, highlightbackground=COLORS["border_subtle"])
                item_frame.pack(fill="x", padx=12, pady=4)
                
                priority_color = COLORS["critical"] if priority["priority"] == 1 else COLORS["warning"]
                tk.Label(item_frame, text=f"●", fg=priority_color, bg=COLORS["bg_secondary"], font=("Segoe UI", 12)).pack(side="left", padx=8, pady=6)
                
                tk.Label(item_frame, text=priority["title"], fg=COLORS["text_white"], bg=COLORS["bg_secondary"], font=FONTS["body_bold"], wraplength=250, justify="left").pack(side="left", fill="x", expand=True, padx=4, pady=6)
                
                def _on_priority_action(pid=priority.get("project_id")):
                    if pid:
                        open_site_manager_module(window, "reports", user_id=user_id, role=role_label)
                
                tk.Button(item_frame, text=priority["action"], bg=COLORS["accent_blue"], fg=COLORS["text_white"], bd=0, relief="flat", font=FONTS["small"], cursor="hand2", padx=6, pady=3).pack(side="right", padx=8, pady=6)
        else:
            tk.Label(priority_card, text="✓ No priorities. Good to go!", fg=COLORS["accent_green"], bg=COLORS["card_bg"], font=FONTS["body"], padx=12, pady=20).pack()
        
        # Center: Alerts
        alerts_card = _create_card(middle_row)
        alerts_card.grid(row=0, column=1, sticky="nsew", padx=8, pady=0)
        
        tk.Label(alerts_card, text="🚨 Alerts", fg=COLORS["accent_red"], bg=COLORS["card_bg"], font=FONTS["h3"]).pack(anchor="w", padx=12, pady=(12, 8))
        
        alerts = get_role_specific_alerts(user_id, role_label)
        if alerts:
            for alert in alerts[:4]:
                alert_bg = COLORS["card_bg"] if alert["severity"] != "critical" else COLORS["bg_secondary"]
                alert_frame = tk.Frame(alerts_card, bg=alert_bg, highlightthickness=1, highlightbackground=alert["severity"] == "critical" and COLORS["critical"] or COLORS["warning"])
                alert_frame.pack(fill="x", padx=12, pady=4)
                
                tk.Label(alert_frame, text=alert["icon"], bg=alert_bg, font=("Segoe UI", 14)).pack(side="left", padx=8, pady=6)
                
                tk.Label(alert_frame, text=alert["title"], fg=COLORS["accent_red"] if alert["severity"] == "critical" else COLORS["text_white"], bg=alert_bg, font=FONTS["body_bold"], wraplength=150, justify="left").pack(side="left", fill="x", expand=True, pady=6)
        else:
            tk.Label(alerts_card, text="✓ All clear!", fg=COLORS["accent_green"], bg=COLORS["card_bg"], font=FONTS["body"], padx=12, pady=20).pack()
        
        # Right: Quick Actions
        actions_card = _create_card(middle_row)
        actions_card.grid(row=0, column=2, sticky="nsew", padx=(8, 0), pady=0)
        
        tk.Label(actions_card, text="⚡ Quick Actions", fg=COLORS["accent_purple"], bg=COLORS["card_bg"], font=FONTS["h3"]).pack(anchor="w", padx=12, pady=(12, 8))
        
        quick_actions = get_quick_actions(role_label)
        for action in quick_actions[:4]:
            def _on_action(action_type=action["action"]):
                if action_type == "new_project":
                    open_site_manager_module(window, "projects", user_id=user_id, role=role_label)
                elif action_type == "submit_report":
                    open_site_manager_module(window, "reports", user_id=user_id, role=role_label)
                elif action_type == "record_attendance":
                    open_site_manager_module(window, "workforce", user_id=user_id, role=role_label)
                elif action_type == "view_projects":
                    open_site_manager_module(window, "projects", user_id=user_id, role=role_label)
                elif action_type == "approve_materials":
                    open_site_manager_module(window, "materials", user_id=user_id, role=role_label)
                elif action_type == "issue_materials":
                    open_site_manager_module(window, "materials", user_id=user_id, role=role_label)
                elif action_type == "admin_users":
                    open_site_manager_module(window, "administration", user_id=user_id, role=role_label)
                else:
                    open_site_manager_module(window, "overview", user_id=user_id, role=role_label)
            
            tk.Button(
                actions_card,
                text=f"{action['icon']} {action['label']}",
                command=_on_action,
                bg=COLORS["accent_blue"],
                fg=COLORS["text_white"],
                bd=0,
                relief="flat",
                padx=12,
                pady=10,
                font=FONTS["body_bold"],
                cursor="hand2",
                wraplength=120,
                justify="center",
            ).pack(fill="x", padx=12, pady=4)
        
        # ─────── BOTTOM ROW: Activity Feed ───────
        activity_card = _create_card(scrollable_frame)
        activity_card.pack(fill="both", expand=True, padx=0, pady=0)
        
        tk.Label(activity_card, text="🕘 Recent Activity", fg=COLORS["accent_teal"], bg=COLORS["card_bg"], font=FONTS["h3"]).pack(anchor="w", padx=12, pady=(12, 8))
        
        activities = get_recent_activity(limit=6)
        if activities:
            for activity in activities[:6]:
                activity_row = tk.Frame(activity_card, bg=COLORS["bg_secondary"], highlightthickness=1, highlightbackground=COLORS["border_subtle"])
                activity_row.pack(fill="x", padx=12, pady=3)
                
                timestamp = activity.get("timestamp", "—")[:16]  # HH:MM format
                activity_type = activity.get("type", "Activity")
                subject = activity.get("subject", "Unknown")
                action = activity.get("action", "—")
                
                tk.Label(activity_row, text=timestamp, fg=COLORS["text_muted"], bg=COLORS["bg_secondary"], font=FONTS["small"], width=12).pack(side="left", padx=8, pady=6)
                
                tk.Label(activity_row, text=f"{activity_type}:", fg=COLORS["accent_teal"], bg=COLORS["bg_secondary"], font=FONTS["body_bold"], width=12).pack(side="left", padx=4, pady=6)
                
                tk.Label(activity_row, text=subject, fg=COLORS["text_white"], bg=COLORS["bg_secondary"], font=FONTS["body"], wraplength=300, justify="left").pack(side="left", padx=4, pady=6, fill="x", expand=True)
                
                if action != "—":
                    tk.Label(activity_row, text=action, fg=COLORS["text_muted"], bg=COLORS["bg_secondary"], font=FONTS["small"]).pack(side="right", padx=8, pady=6)
        else:
            tk.Label(activity_card, text="No recent activity yet.", fg=COLORS["text_muted"], bg=COLORS["card_bg"], font=FONTS["body"], padx=12, pady=20).pack()
        
        # Add scroll support
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    _render_main_content()
    
    if should_mainloop:
        window.mainloop()
