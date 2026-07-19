"""Equipment and plant management surface for JEPA Site Manager."""

import tkinter as tk

from ui.themes import FONTS


def open_equipment_view(parent: tk.Misc) -> None:
    """Open a lightweight equipment management view."""
    win = tk.Toplevel(parent)
    win.title("JEPA Site Manager — Equipment")
    win.geometry("760x420")
    win.configure(bg="#0F172A")

    tk.Label(win, text="EQUIPMENT & PLANT STATUS", fg="#06B6D4", bg="#0F172A", font=FONTS["h2"]).pack(pady=(18, 6))
    tk.Label(win, text="Monitor equipment availability, maintenance status, and field readiness.", fg="#CBD5E1", bg="#0F172A", font=FONTS["small"]).pack()

    cards = tk.Frame(win, bg="#0F172A")
    cards.pack(fill="both", expand=True, padx=18, pady=16)

    def _card(title: str, value: str, accent: str):
        frame = tk.Frame(cards, bg="#111827", highlightthickness=1, highlightbackground=accent)
        frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(frame, text=title, fg="#E2E8F0", bg="#111827", font=FONTS["label"]).pack(anchor="w", padx=12, pady=(10, 4))
        tk.Label(frame, text=value, fg="#F8FAFC", bg="#111827", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=12, pady=(0, 10))

    _card("Fleet Available", "18", "#22C55E")
    _card("In Maintenance", "3", "#F59E0B")
    _card("Fuel Level", "76%", "#06B6D4")
    _card("Critical Assets", "2", "#EF4444")
