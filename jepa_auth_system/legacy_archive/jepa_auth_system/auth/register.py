"""
auth/register.py — Multi-step registration form with full validation.
"""
import tkinter as tk
from tkinter import ttk

from database.db import get_connection
from auth.security import hash_password, hash_answer, generate_recovery_code, is_valid_admin_code
from auth.validators import (
    is_strong_password, is_valid_email, is_valid_username,
    is_valid_phone, password_strength_label,
    normalise_username, normalise_email, PASSWORD_HINT,
)
from ui.themes import FONTS, SECURITY_QUESTIONS
from ui.components import (
    form_label, form_entry, password_entry, action_button,
    status_label, country_combobox, COUNTRY_LIST,
)
from utils.logger import log_activity


def open_register_window(parent_root: tk.Tk, on_success_callback):
    """Open the registration window. Calls on_success_callback() when done."""
    parent_root.withdraw()

    win = tk.Toplevel()
    win.title("Create Account — JEPA")
    win.geometry("420x740")
    win.resizable(False, False)

    t = {"bg": "#0F172A", "panel": "#1E293B", "fg": "#F8FAFC",
         "lbl_sub": "#94A3B8", "input_bg": "#334155", "border": "#334155",
         "accent": "#0EA5E9", "accent_hover": "#38BDF8",
         "success": "#10B981", "error": "#EF4444",
         "btn_sec": "#1E293B", "btn_sec_fg": "#94A3B8"}

    win.configure(bg=t["bg"])

    # Scroll container
    canvas = tk.Canvas(win, bg=t["bg"], bd=0, highlightthickness=0)
    scrollbar = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg=t["bg"])
    scroll_frame.bind("<Configure>", lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Bind mousewheel
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # ── Header ────────────────────────────────────────────────────────────────
    tk.Label(scroll_frame, text="JEPA WORKSPACE",
             fg=t["accent"], bg=t["bg"], font=FONTS["brand"]).pack(pady=(25, 2))
    tk.Label(scroll_frame, text="Create Your Account",
             fg=t["fg"], bg=t["bg"], font=FONTS["h1"]).pack(pady=(0, 5))

    status_lbl = status_label(scroll_frame, t)

    # ── Form variables ────────────────────────────────────────────────────────
    v = {k: tk.StringVar() for k in [
        "username", "email", "phone", "password", "confirm_password",
        "full_name", "gender", "dob", "bio",
        "role", "admin_code", "security_question", "security_answer",
        "country_combo",
    ]}
    v["role"].set("user")
    v["gender"].set("Prefer not to say")

    def _lbl(text):
        form_label(scroll_frame, text, t)

    # Username
    _lbl("USERNAME")
    form_entry(scroll_frame, v["username"], t)

    # Email
    _lbl("EMAIL ADDRESS")
    form_entry(scroll_frame, v["email"], t)

    # Phone
    _lbl("PHONE NUMBER")
    phone_frame = tk.Frame(scroll_frame, bg=t["bg"])
    phone_frame.pack(fill="x", padx=45, pady=(0, 0))
    country_combobox(phone_frame, v["country_combo"]).pack(
        side="left", ipady=2, padx=(0, 5))
    tk.Entry(phone_frame, textvariable=v["phone"],
             font=FONTS["body"], bg=t["input_bg"], fg=t["fg"],
             insertbackground=t["fg"], bd=0
             ).pack(side="left", fill="x", expand=True, ipady=5)

    # Password
    _lbl("PASSWORD")
    _, _ = password_entry(scroll_frame, v["password"], t)

    # Strength indicator
    strength_lbl = tk.Label(scroll_frame, text="", font=FONTS["small_bold"],
                            bg=t["bg"], fg=t["lbl_sub"])
    strength_lbl.pack(padx=45, anchor="w")

    def _update_strength(*_):
        label, colour = password_strength_label(v["password"].get())
        strength_lbl.config(text=label, fg=colour)

    v["password"].trace_add("write", _update_strength)

    # Confirm password
    _lbl("CONFIRM PASSWORD")
    password_entry(scroll_frame, v["confirm_password"], t)

    # Full name (optional)
    _lbl("FULL NAME (OPTIONAL)")
    form_entry(scroll_frame, v["full_name"], t)

    # Gender & DOB on one row
    dem_lbl_frame = tk.Frame(scroll_frame, bg=t["bg"])
    dem_lbl_frame.pack(fill="x", padx=45, pady=(10, 2))
    tk.Label(dem_lbl_frame, text="GENDER", fg=t["lbl_sub"], bg=t["bg"],
             font=FONTS["label"]).pack(side="left", fill="x", expand=True)
    tk.Label(dem_lbl_frame, text="DATE OF BIRTH", fg=t["lbl_sub"], bg=t["bg"],
             font=FONTS["label"]).pack(side="left", fill="x", expand=True)

    dem_input_frame = tk.Frame(scroll_frame, bg=t["bg"])
    dem_input_frame.pack(fill="x", padx=45)
    ttk.Combobox(dem_input_frame, textvariable=v["gender"],
                 values=["Male", "Female", "Other", "Prefer not to say"],
                 font=FONTS["body"], state="readonly", width=14
                 ).pack(side="left", expand=True, ipady=2)
    tk.Entry(dem_input_frame, textvariable=v["dob"],
             font=FONTS["body"], bg=t["input_bg"], fg=t["fg"],
             insertbackground=t["fg"], bd=0
             ).pack(side="left", fill="x", expand=True, padx=(5, 0), ipady=5)
    tk.Label(scroll_frame, text="Format: DD/MM/YYYY",
             fg=t["lbl_sub"], bg=t["bg"], font=FONTS["small"]
             ).pack(padx=45, anchor="w")

    # Bio (optional)
    _lbl("SHORT BIO (OPTIONAL)")
    form_entry(scroll_frame, v["bio"], t)

    # Security question
    _lbl("SECURITY QUESTION")
    ttk.Combobox(scroll_frame, textvariable=v["security_question"],
                 values=SECURITY_QUESTIONS,
                 font=FONTS["small"], state="readonly"
                 ).pack(fill="x", padx=45, ipady=3, pady=(0, 0))

    _lbl("SECURITY ANSWER")
    form_entry(scroll_frame, v["security_answer"], t)

    # Role selector
    _lbl("ACCOUNT ROLE")
    role_frame = tk.Frame(scroll_frame, bg=t["bg"])
    role_frame.pack(padx=45, anchor="w")
    for r in ("user", "admin"):
        tk.Radiobutton(role_frame, text=r.capitalize(), variable=v["role"],
                       value=r, bg=t["bg"], fg=t["fg"], selectcolor=t["input_bg"],
                       activebackground=t["bg"], font=FONTS["body"]
                       ).pack(side="left", padx=(0, 15))

    _lbl("ADMIN CODE (ADMIN ACCOUNTS ONLY)")
    admin_ent = form_entry(scroll_frame, v["admin_code"], t, show="•")

    # ── Register action ────────────────────────────────────────────────────────
    def _register():
        status_lbl.config(text="", fg=t["error"])

        username  = normalise_username(v["username"].get())
        email     = normalise_email(v["email"].get())
        phone     = v["phone"].get().strip()
        password  = v["password"].get()
        confirm   = v["confirm_password"].get()
        role      = v["role"].get()
        admin_code= v["admin_code"].get()
        sec_q     = v["security_question"].get()
        sec_a     = v["security_answer"].get().strip()

        # Extract country code from combo
        combo_val = v["country_combo"].get()
        country_code = combo_val.split("(")[-1].replace(")", "").strip() if "(" in combo_val else "+256"

        # Validations
        if not is_valid_username(username):
            status_lbl.config(text="Username: 3–30 chars, letters/digits/_ only.")
            return
        if not is_valid_email(email):
            status_lbl.config(text="Please enter a valid email address.")
            return
        if not is_valid_phone(phone):
            status_lbl.config(text="Phone: digits only, 7–15 characters.")
            return
        if not is_strong_password(password):
            status_lbl.config(text=PASSWORD_HINT)
            return
        if password != confirm:
            status_lbl.config(text="Passwords do not match.")
            return
        if role == "admin" and not is_valid_admin_code(admin_code):
            status_lbl.config(text="Invalid admin registration code.")
            return
        if not sec_q:
            status_lbl.config(text="Please select a security question.")
            return
        if len(sec_a) < 2:
            status_lbl.config(text="Security answer is too short.")
            return

        try:
            pw_hash       = hash_password(password)
            answer_hash   = hash_answer(sec_a)
            recovery_code = generate_recovery_code()

            with get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO users
                        (username, email, phone, password_hash, role,
                         full_name, country_code, gender, dob, bio,
                         security_question, security_answer_hash, recovery_code)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        username, email, country_code + phone, pw_hash, role,
                        v["full_name"].get().strip() or None,
                        country_code,
                        v["gender"].get(),
                        v["dob"].get().strip() or None,
                        v["bio"].get().strip() or None,
                        sec_q, answer_hash, recovery_code,
                    ),
                )
                conn.commit()
                user_id = conn.execute(
                    "SELECT id FROM users WHERE username = ?", (username,)
                ).fetchone()["id"]

            log_activity("Registration", user_id=user_id, username=username,
                         details=f"Role: {role}")

            # Show recovery code to user
            status_lbl.config(
                fg=t["success"],
                text=(f"Account created! Your recovery code:\n{recovery_code}\n"
                      "Save this somewhere safe. Click Sign In to continue."),
            )

        except Exception as exc:
            if "UNIQUE" in str(exc):
                if "username" in str(exc):
                    status_lbl.config(text="Username already taken.")
                elif "email" in str(exc):
                    status_lbl.config(text="Email already registered.")
                elif "phone" in str(exc):
                    status_lbl.config(text="Phone number already registered.")
                else:
                    status_lbl.config(text="An account with those details exists.")
            else:
                status_lbl.config(text=f"Error: {exc}")

    def _back_to_login():
        canvas.unbind_all("<MouseWheel>")
        win.destroy()
        parent_root.deiconify()

    action_button(scroll_frame, "Create Account", _register, t, "primary")
    action_button(scroll_frame, "← Back to Sign In", _back_to_login, t, "secondary")
    tk.Frame(scroll_frame, height=20, bg=t["bg"]).pack()  # bottom spacer

    win.protocol("WM_DELETE_WINDOW", _back_to_login)
    win.mainloop()
