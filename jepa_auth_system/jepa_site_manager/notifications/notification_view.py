"""Notification center placeholder for JEPA Site Manager."""

import tkinter as tk

from ui.themes import FONTS


def open_notifications_view(parent: tk.Misc) -> None:
    """Open a placeholder notifications workspace."""
    win = tk.Toplevel(parent)
    win.title("JEPA Site Manager — Notifications")
    win.geometry("840x420")
    win.configure(bg="#0F172A")

    tk.Label(win, text="NOTIFICATIONS & ALERTS", fg="#0EA5E9", bg="#0F172A", font=FONTS["h2"]).pack(pady=(18, 6))
    tk.Label(win, text="Operational alerts and reminders will be surfaced here.", fg="#94A3B8", bg="#0F172A", font=FONTS["small"]).pack()
    tk.Label(win, text="This placeholder preserves navigation while notifications are built out.", fg="#E2E8F0", bg="#0F172A", font=FONTS["body"]).pack(padx=18, pady=(12, 0), anchor="w")
