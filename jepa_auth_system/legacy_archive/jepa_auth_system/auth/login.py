"""
auth/login.py — Login window: accepts username, email, or phone.
"""
import tkinter as tk

from database.db import get_connection
from auth.security import verify_password, verify_totp  # <--- Updated Import
from ui.themes import FONTS
from ui.components import password_entry, status_label
from utils.logger import log_activity
from utils.mailer import send_security_alert  # <--- New Import


def login_window():
    root = tk.Tk()
    root.title("JEPA — Sign In")
    root.geometry("400x560")
    root.resizable(False, False)

    try:
        from ui.components import resolve_asset
        root.iconbitmap(str(resolve_asset("app_icon.ico")))
    except Exception:
        pass

    t = {"bg": "#0F172A", "panel": "#1E293B", "fg": "#F8FAFC",
         "lbl_sub": "#94A3B8", "input_bg": "#334155",
         "accent": "#0EA5E9", "accent_hover": "#38BDF8",
         "success": "#10B981", "error": "#EF4444",
         "btn_sec": "#1E293B", "btn_sec_fg": "#94A3B8"}

    root.configure(bg=t["bg"])

    # ── Header ─────────────────────────────────────────────────────────────────
    tk.Label(root, text="JEPA WORKSPACE",
             fg=t["accent"], bg=t["bg"], font=FONTS["brand"]).pack(pady=(30, 2))
    tk.Label(root, text="Sign in to your secure workspace panel.",
             fg=t["lbl_sub"], bg=t["bg"], font=FONTS["small"]).pack(pady=(0, 24))

    # ── Form Fields ────────────────────────────────────────────────────────────
    tk.Label(root, text="USERNAME, EMAIL, OR PHONE", fg=t["lbl_sub"], bg=t["bg"],
             font=FONTS["label"]).pack(fill="x", padx=45, pady=(8, 2))
    
    v_identity = tk.StringVar()
    entry_id = tk.Entry(root, textvariable=v_identity, font=FONTS["body"],
                        bg=t["input_bg"], fg=t["fg"], bd=0, insertbackground=t["fg"])
    entry_id.pack(fill="x", padx=45, ipady=5)
    entry_id.focus_set()

    tk.Label(root, text="PASSWORD", fg=t["lbl_sub"], bg=t["bg"],
             font=FONTS["label"]).pack(fill="x", padx=45, pady=(14, 2))
    
    v_password = tk.StringVar()
    password_entry(root, v_password, t)

    status_lbl = status_label(root, t)

    def _sign_in(event=None):
        status_lbl.config(text="", fg=t["error"])
        identity = v_identity.get().strip()
        password = v_password.get()

        if not identity or not password:
            status_lbl.config(text="Please fill in all security fields.")
            return

        with get_connection() as conn:
            row = conn.execute(
                """SELECT id, username, email, password_hash, role, status, theme, totp_secret 
                   FROM users 
                   WHERE username = ? OR email = ? OR phone = ?""",
                (identity, identity, identity)
            ).fetchone()

        if not row:
            status_lbl.config(text="Invalid credentials. Match not found.")
            return

        if row["status"] == "suspended":
            status_lbl.config(text="This account has been administratively suspended.")
            return

        if not verify_password(password, row["password_hash"]):
            status_lbl.config(text="Incorrect password. Please try again.")
            return

        log_activity("Login Attempt", user_id=row["id"], username=row["username"])

        # INTERCEPT WITH 2FA CHALLENGE IF SET UP
        if row["totp_secret"]:
            _open_2fa_verification_modal(root, row, t)
            return

        # Regular path if 2FA is not active yet
        root.destroy()
        if row["role"] == "admin":
            from dashboard.admin_dashboard import admin_dashboard
            admin_dashboard(row["id"], row["username"], row["theme"])
        else:
            from dashboard.user_dashboard import user_dashboard
            user_dashboard(row["id"], row["username"], row["theme"])

    # ── Buttons ────────────────────────────────────────────────────────────────
    tk.Button(root, text="Sign In Securely", command=_sign_in,
              bg=t["accent"], fg="white", font=FONTS["body_bold"],
              bd=0, cursor="hand2"
              ).pack(fill="x", padx=45, pady=(22, 8), ipady=5)

    def _go_register():
        from auth.register import open_register_window
        open_register_window(root, on_success_callback=None)

    tk.Button(root, text="Create New Account", command=_go_register,
              bg=t["btn_sec"], fg=t["btn_sec_fg"],
              font=FONTS["body"], bd=0, cursor="hand2"
              ).pack(fill="x", padx=45, ipady=4)

    def _go_forgot():
        from auth.forgot_password import open_forgot_password
        open_forgot_password(root)

    tk.Label(root, text="Forgot your password?",
             fg=t["accent"], bg=t["bg"], font=FONTS["small"],
             cursor="hand2"
             ).pack(pady=(14, 0))

    root.bind_all("<Return>", _sign_in)


def _open_2fa_verification_modal(parent_root, user_row, theme_dict):
    """Blocks main window progression until valid 2FA input is submitted."""
    t = theme_dict
    modal = tk.Toplevel(parent_root)
    modal.title("2FA Challenge")
    modal.geometry("340x240")
    modal.resizable(False, False)
    modal.configure(bg=t["bg"])
    modal.grab_set()

    tk.Label(modal, text="Two-Factor Check", fg=t["accent"], bg=t["bg"], font=("Segoe UI", 14, "bold")).pack(pady=(20, 5))
    tk.Label(modal, text="Enter the code from your Authenticator App:", fg=t["lbl_sub"], bg=t["bg"], font=("Segoe UI", 9)).pack(pady=(0, 15))

    v_code = tk.StringVar()
    err_lbl = tk.Label(modal, text="", fg=t["error"], bg=t["bg"], font=("Segoe UI", 9, "bold"))
    err_lbl.pack()

    entry = tk.Entry(modal, textvariable=v_code, font=("Consolas", 12), bg=t["input_bg"], fg=t["fg"], justify="center", bd=0)
    entry.pack(fill="x", padx=60, ipady=6, pady=10)
    entry.focus_set()

    def _validate():
        if verify_totp(user_row["totp_secret"], v_code.get()):
            modal.destroy()
            parent_root.destroy()
            
            if user_row["email"]:
                send_security_alert(user_row["email"], "Successful Authorization", "Account accessed via verified 2FA token check.")
            
            if user_row["role"] == "admin":
                from dashboard.admin_dashboard import admin_dashboard
                admin_dashboard(user_row["id"], user_row["username"], user_row["theme"])
            else:
                from dashboard.user_dashboard import user_dashboard
                user_dashboard(user_row["id"], user_row["username"], user_row["theme"])
        else:
            err_lbl.config(text="Invalid 2FA token code. Please retry.")

    tk.Button(modal, text="Confirm Access", command=_validate, bg=t["accent"], fg="white", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2").pack(fill="x", padx=60, pady=15, ipady=4)
    modal.bind("<Return>", lambda e: _validate())