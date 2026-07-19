"""
ui/splash.py — Animated JEPA splash screen with fade in/out.
"""
import tkinter as tk
from PIL import Image, ImageTk
from ui.components import resolve_asset


def splash_screen():
    splash = tk.Tk()
    splash.overrideredirect(True)

    # Centre the splash window
    sw = splash.winfo_screenwidth()
    sh = splash.winfo_screenheight()
    w, h = 440, 320
    splash.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")
    splash.configure(bg="#0F172A")
    splash.attributes("-alpha", 0.0)

    # Logo
    try:
        logo_path = resolve_asset("JEPA DESIGN LOGO.png")
        logo_img  = Image.open(logo_path).resize((150, 150), Image.Resampling.LANCZOS)
        logo      = ImageTk.PhotoImage(logo_img)
        lbl_logo  = tk.Label(splash, image=logo, bg="#0F172A")
        lbl_logo.image = logo
        lbl_logo.pack(pady=(40, 10))
    except Exception:
        tk.Label(splash, text="JEPA", fg="#0EA5E9", bg="#0F172A",
                 font=("Segoe UI", 30, "bold")).pack(pady=(50, 10))

    tk.Label(splash, text="JEPA Site Manager",
             fg="#F8FAFC", bg="#0F172A",
             font=("Segoe UI", 14, "bold")).pack()

    tk.Label(splash, text="Project, reports, materials, and site operations…",
             fg="#94A3B8", bg="#0F172A",
             font=("Segoe UI", 9)).pack(pady=(8, 0))

    # Progress bar
    progress_canvas = tk.Canvas(splash, width=280, height=4,
                                bg="#1E293B", bd=0, highlightthickness=0)
    progress_canvas.pack(pady=(20, 0))
    progress_bar = progress_canvas.create_rectangle(0, 0, 0, 4, fill="#0EA5E9", width=0)

    def _animate_progress(step=0):
        if step <= 280:
            progress_canvas.coords(progress_bar, 0, 0, step, 4)
            splash.after(8, lambda: _animate_progress(step + 4))

    def fade_in(alpha=0.0):
        if alpha < 1.0:
            splash.attributes("-alpha", alpha + 0.06)
            splash.after(25, lambda: fade_in(alpha + 0.06))
        else:
            _animate_progress()
            splash.after(2200, fade_out)

    def fade_out(alpha=1.0):
        if alpha > 0.0:
            splash.attributes("-alpha", max(0.0, alpha - 0.06))
            splash.after(25, lambda: fade_out(alpha - 0.06))
        else:
            splash.destroy()
            from auth.login import login_window
            login_window()

    fade_in()
    splash.mainloop()
