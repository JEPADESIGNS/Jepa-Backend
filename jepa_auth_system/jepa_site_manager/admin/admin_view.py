"""Administration workspace placeholder for JEPA Site Manager."""

import tkinter as tk

from ui.themes import FONTS


def open_admin_workspace(parent: tk.Misc, user_id: int | None = None) -> None:
    """Open a placeholder administration workspace."""
    win = tk.Toplevel(parent)
    win.title("JEPA Site Manager — Administration")
    win.geometry("900x460")
    win.configure(bg="#0F172A")

    tk.Label(win, text="ADMINISTRATION WORKSPACE", fg="#0EA5E9", bg="#0F172A", font=FONTS["h2"]).pack(pady=(18, 6))
    tk.Label(win, text="User, role, and audit log management will be available here.", fg="#94A3B8", bg="#0F172A", font=FONTS["small"]).pack()
    tk.Label(win, text="This placeholder preserves the role-based command center path while the admin features are built.", fg="#E2E8F0", bg="#0F172A", font=FONTS["body"]).pack(padx=18, pady=(12, 0), anchor="w")
