"""
ui/components.py — Reusable Tkinter widgets for the JEPA Auth system.
"""
import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageOps

from ui.themes import FONTS, COUNTRY_LIST


# ── Asset resolution ───────────────────────────────────────────────────────────

import sys
from pathlib import Path


def resolve_asset(name: str) -> Path:
    if hasattr(sys, "_MEIPASS"):
        p = Path(sys._MEIPASS) / "assets" / name
        if p.exists():
            return p
    base = Path(__file__).resolve().parent.parent
    for candidate in [
        base / "assets" / name,
        Path.cwd() / "assets" / name,
        Path.home() / ".jepa_auth" / "assets" / name,
    ]:
        if candidate.exists():
            return candidate
    # Fallback: create a blank placeholder
    fallback = Path.home() / ".jepa_auth" / "assets" / name
    fallback.parent.mkdir(parents=True, exist_ok=True)
    if not fallback.exists() and name.endswith(".png"):
        Image.new("RGB", (180, 180), color=(71, 85, 105)).save(fallback)
    return fallback


# ── Circular avatar helper ─────────────────────────────────────────────────────

def get_circular_avatar(
    image_path: str | None,
    size: tuple[int, int] = (110, 110),
    bg_color: str = "#1E293B",
) -> ImageTk.PhotoImage:
    try:
        if image_path and os.path.exists(image_path):
            img = Image.open(image_path).convert("RGBA")
        else:
            img = Image.new("RGBA", size, color="#475569")

        img = ImageOps.fit(img, size, Image.Resampling.LANCZOS)
        mask = Image.new("L", size, 0)
        ImageDraw.Draw(mask).ellipse((0, 0) + size, fill=255)

        solid_bg = Image.new("RGBA", size, bg_color)
        solid_bg.paste(img, (0, 0), mask=mask)
        return ImageTk.PhotoImage(solid_bg.convert("RGB"))
    except Exception:
        return ImageTk.PhotoImage(Image.new("RGB", size, color=bg_color))


# ── Form helpers ───────────────────────────────────────────────────────────────

def form_label(parent: tk.Widget, text: str, theme: dict) -> tk.Label:
    lbl = tk.Label(
        parent, text=text,
        fg=theme["lbl_sub"], bg=theme["bg"],
        font=FONTS["label"],
    )
    lbl.pack(fill="x", padx=45, pady=(10, 2))
    return lbl


def form_entry(
    parent: tk.Widget,
    var: tk.StringVar,
    theme: dict,
    show: str = "",
) -> tk.Entry:
    ent = tk.Entry(
        parent, textvariable=var, show=show,
        font=FONTS["body"],
        bg=theme["input_bg"], fg=theme["fg"],
        insertbackground=theme["fg"], bd=0,
        relief="flat",
    )
    ent.pack(fill="x", padx=45, ipady=5)
    return ent


def password_entry(
    parent: tk.Widget,
    var: tk.StringVar,
    theme: dict,
) -> tuple[tk.Entry, tk.Button]:
    """Entry with show/hide toggle. Returns (entry, toggle_button)."""
    frame = tk.Frame(parent, bg=theme["input_bg"])
    frame.pack(fill="x", padx=45)

    ent = tk.Entry(
        frame, textvariable=var, show="*",
        font=FONTS["body"],
        bg=theme["input_bg"], fg=theme["fg"],
        insertbackground=theme["fg"], bd=0,
    )
    ent.pack(side="left", fill="x", expand=True, ipady=5, padx=(5, 0))

    def toggle():
        if ent.cget("show") == "*":
            ent.config(show="")
            btn.config(text="Hide")
        else:
            ent.config(show="*")
            btn.config(text="Show")

    btn = tk.Button(
        frame, text="Show", command=toggle,
        bg=theme["input_bg"], fg=theme["lbl_sub"],
        font=FONTS["small_bold"], bd=0, cursor="hand2",
    )
    btn.pack(side="right", padx=5, pady=2, ipadx=4)
    return ent, btn


def action_button(
    parent: tk.Widget,
    text: str,
    command,
    theme: dict,
    style: str = "primary",
) -> tk.Button:
    colours = {
        "primary": (theme["accent"],   "white"),
        "success": (theme["success"],  "white"),
        "danger":  (theme["error"],    "white"),
        "secondary":(theme["btn_sec"], theme["btn_sec_fg"]),
    }
    bg, fg = colours.get(style, colours["primary"])
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=fg,
        font=FONTS["body_bold"], bd=0, cursor="hand2",
        relief="flat", activebackground=theme["accent_hover"],
    )
    btn.pack(fill="x", padx=45, pady=(8, 4), ipady=5)
    return btn


def status_label(parent: tk.Widget, theme: dict) -> tk.Label:
    """A shared label for inline success / error messages."""
    lbl = tk.Label(
        parent, text="",
        fg=theme["error"], bg=theme["bg"],
        font=FONTS["small_bold"],
        wraplength=310, justify="center",
    )
    lbl.pack(pady=(2, 0))
    return lbl


def country_combobox(
    parent: tk.Widget,
    var: tk.StringVar,
    default_code: str = "+256",
) -> ttk.Combobox:
    default_idx = next(
        (i for i, c in enumerate(COUNTRY_LIST) if default_code in c), 0
    )
    cb = ttk.Combobox(
        parent, textvariable=var,
        values=COUNTRY_LIST,
        font=FONTS["body"],
        width=20,
    )
    cb.current(default_idx)

    def _filter(event):
        typed = cb.get()
        cb["values"] = (
            COUNTRY_LIST if not typed
            else [c for c in COUNTRY_LIST if typed.lower() in c.lower()]
        )
        cb.event_generate("<Down>")

    cb.bind("<KeyRelease>", _filter)
    return cb
