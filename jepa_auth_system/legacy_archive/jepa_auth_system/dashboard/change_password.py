"""
dashboard/change_password.py — Change password dialog for logged-in users.
"""
import tkinter as tk
from database.db import get_connection
from auth.security import verify_password, hash_password
from auth.validators import is_strong_password, PASSWORD_HINT
from ui.themes import FONTS
from ui.components import password_entry, status_label
from utils.logger import log_activity
from utils.mailer import send_security_alert  # <--- New Import

def open_change_password(parent, user_id: int, username: str, theme: dict):
    win = tk.Toplevel(parent)
    win.title("Change Password")
    win.geometry("380x420")
    win.resizable(False, False)
    win.configure(bg=theme["bg"])
    win.grab_set()

    t = theme

    tk.Label(win, text="Change Password",
             fg=t["fg"], bg=t["bg"], font=FONTS["h2"]).pack(pady=(20, 5))

    status_lbl = status_label(win, t)

    v = {k: tk.StringVar() for k in ["current", "new", "confirm"]}

    for label_text, key in [
        ("CURRENT PASSWORD", "current"),
        ("NEW PASSWORD", "new"),
        ("CONFIRM NEW PASSWORD", "confirm"),
    ]:
        tk.Label(win, text=label_text, fg=t["lbl_sub"], bg=t["bg"],
                 font=FONTS["label"]).pack(fill="x", padx=40, pady=(12, 2))
        password_entry(win, v[key], t)

    def _save():
        status_lbl.config(text="", fg=t["error"])
        
        with get_connection() as conn:
            row = conn.execute(
                "SELECT email, password_hash FROM users WHERE id=?", (user_id,)
            ).fetchone()

        if not verify_password(v["current"].get(), row["password_hash"]):
            status_lbl.config(text="Current password is incorrect.")
            return
        if not is_strong_password(v["new"].get()):
            status_lbl.config(text=PASSWORD_HINT)
            return
        if v["new"].get() != v["confirm"].get():
            status_lbl.config(text="New passwords do not match.")
            return

        with get_connection() as conn:
            conn.execute(
                "UPDATE users SET password_hash=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (hash_password(v["new"].get()), user_id),
            )
            conn.commit()

        # TRIGGER EMAIL ALERT
        if row["email"]:
            send_security_alert(
                row["email"], 
                "Password Changed", 
                f"The password for account '{username}' was successfully updated."
            )

        log_activity("Password Changed", user_id=user_id, username=username)
        status_lbl.config(fg=t["success"], text="Password updated successfully.")

    tk.Button(win, text="Save New Password", command=_save,
              bg=t["accent"], fg="white", font=FONTS["body_bold"],
              bd=0, cursor="hand2"
              ).pack(fill="x", padx=40, pady=(20, 0), ipady=5)
    
    tk.Button(win, text="Cancel", command=win.destroy,
              bg=t["btn_sec"], fg=t["btn_sec_fg"],
              font=FONTS["body"], bd=0
              ).pack(fill="x", padx=40, pady=(10, 0), ipady=4)