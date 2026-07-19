"""
dashboard/profile.py — Profile editor dialog with database integrity checking.
"""
import tkinter as tk
import sqlite3
from database.db import get_connection
from ui.themes import FONTS
from ui.components import status_label


def open_profile_editor(parent, user_id: int, username: str, theme: dict, on_save_callback):
    win = tk.Toplevel(parent)
    win.title("Edit Profile Details")
    win.geometry("400x580")
    win.resizable(False, False)
    win.configure(bg=theme["bg"])
    win.grab_set()

    t = theme

    tk.Label(win, text="Update Profile", fg=t["fg"], bg=t["bg"], font=FONTS["h2"]).pack(pady=(20, 5))
    status_lbl = status_label(win, t)

    # Fetch existing data to pre-populate inputs
    with get_connection() as conn:
        row = conn.execute(
            "SELECT full_name, phone, gender, dob, bio FROM users WHERE id=?", (user_id,)
        ).fetchone()

    fields = ["full_name", "phone", "gender", "dob", "bio"]
    v = {k: tk.StringVar(value=str(row[k]) if row and row[k] else "") for k in fields}

    # Draw inputs block
    for label_text, key in [
        ("FULL NAME", "full_name"),
        ("PHONE NUMBER", "phone"),
        ("GENDER", "gender"),
        ("DATE OF BIRTH (YYYY-MM-DD)", "dob"),
        ("BIOGRAPHY SUMMARY", "bio"),
    ]:
        tk.Label(win, text=label_text, fg=t["lbl_sub"], bg=t["bg"], font=FONTS["label"]).pack(fill="x", padx=40, pady=(10, 2))
        
        if key == "bio":
            entry = tk.Entry(win, textvariable=v[key], font=FONTS["body"], bg=t["input_bg"], fg=t["fg"], bd=0)
        else:
            entry = tk.Entry(win, textvariable=v[key], font=FONTS["body"], bg=t["input_bg"], fg=t["fg"], bd=0)
        entry.pack(fill="x", padx=40, ipady=5)

    def _save():
        status_lbl.config(text="", fg=t["error"])
        
        # Clean up double country codes if accidentally appended
        phone_input = v["phone"].get().strip()
        if phone_input.startswith("+256 +256"):
            phone_input = phone_input.replace("+256 +256", "+256")

        try:
            with get_connection() as conn:
                conn.execute(
                    """UPDATE users 
                       SET full_name=?, phone=?, gender=?, dob=?, bio=?, updated_at=CURRENT_TIMESTAMP 
                       WHERE id=?""",
                    (v["full_name"].get().strip(),
                     phone_input,
                     v["gender"].get().strip(),
                     v["dob"].get().strip(),
                     v["bio"].get().strip(),
                     user_id)
                )
                conn.commit()
            
            status_lbl.config(fg=t["success"], text="Profile changes successfully synchronized.")
            if on_save_callback:
                on_save_callback()
                
        except sqlite3.IntegrityError as e:
            # Safely handle the unique constraint violation without crashing
            if "users.phone" in str(e):
                status_lbl.config(text="Error: This phone number is already linked to another account.")
            else:
                status_lbl.config(text="Error: Data conflict constraint broken.")

    tk.Button(win, text="Save Changes", command=_save,
              bg=t["accent"], fg="white", font=FONTS["body_bold"],
              bd=0, cursor="hand2"
              ).pack(fill="x", padx=40, pady=(24, 0), ipady=5)
    
    tk.Button(win, text="Discard", command=win.destroy,
              bg=t["btn_sec"], fg=t["btn_sec_fg"],
              font=FONTS["body"], bd=0, cursor="hand2"
              ).pack(fill="x", padx=40, pady=(10, 0), ipady=4)