"""Placeholder BOQ view for JEPA Site Manager."""

import tkinter as tk

from ui.themes import FONTS


def open_boq_view(parent: tk.Misc) -> None:
    """Open a simple placeholder BOQ / cost screen."""
    win = tk.Toplevel(parent)
    win.title("JEPA Site Manager — BOQ & Costs")
    win.geometry("720x400")
    win.configure(bg="#0F172A")

    tk.Label(win, text="BOQ & COSTS", fg="#0EA5E9", bg="#0F172A", font=FONTS["h2"]).pack(pady=(18, 6))
    tk.Label(win, text="BOQ and cost tracking will be connected here in the next incremental step.", fg="#94A3B8", bg="#0F172A", font=FONTS["small"]).pack(pady=(0, 18))
    tk.Label(win, text="This placeholder keeps the dashboard entry point working while the real cost workflow is added.", fg="#E2E8F0", bg="#0F172A", font=FONTS["body"]).pack(padx=18, anchor="w")
