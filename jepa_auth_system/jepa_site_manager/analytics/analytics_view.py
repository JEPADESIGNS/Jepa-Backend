"""Placeholder analytics view for JEPA Site Manager."""

import tkinter as tk

from ui.themes import FONTS


def open_analytics_view(parent: tk.Misc) -> None:
    """Open a simple placeholder analytics screen."""
    win = tk.Toplevel(parent)
    win.title("JEPA Site Manager — Analytics")
    win.geometry("720x400")
    win.configure(bg="#0F172A")

    tk.Label(win, text="ANALYTICS", fg="#0EA5E9", bg="#0F172A", font=FONTS["h2"]).pack(pady=(18, 6))
    tk.Label(win, text="Analytics and reporting summaries will be added here next.", fg="#94A3B8", bg="#0F172A", font=FONTS["small"]).pack(pady=(0, 18))
    tk.Label(win, text="This placeholder keeps the dashboard entry path available during incremental development.", fg="#E2E8F0", bg="#0F172A", font=FONTS["body"]).pack(padx=18, anchor="w")
