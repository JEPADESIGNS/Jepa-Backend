"""
dashboard/profile.py — Profile editor dialog with database integrity checking.
"""
import os
import sqlite3
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from PIL import Image, ImageOps

from database.db import get_connection
from ui.components import get_circular_avatar, status_label
from ui.themes import FONTS
from jepa_site_manager.auth.roles import USER_ROLES, normalize_role, get_role_label
from dashboard import get_role_label as get_role_label_dashboard


def open_profile_editor(parent, user_id: int, username: str, theme: dict, on_save_callback):
    win = tk.Toplevel(parent)
    win.title("Edit Profile Details")
    win.geometry("430x680")
    win.resizable(False, False)
    win.configure(bg=theme["bg"])
    win.grab_set()

    t = theme

    # Fetch existing data to pre-populate inputs
    with get_connection() as conn:
        row = conn.execute(
            "SELECT profile_pic, full_name, phone, gender, dob, bio, role, status FROM users WHERE id=?",
            (user_id,),
        ).fetchone()

    tk.Label(win, text="Update Profile", fg=t["fg"], bg=t["bg"], font=FONTS["h2"]).pack(pady=(18, 5))
    role_text = get_role_label(row.get("role") if row and "role" in row else "user")
    status_text = (row.get("status") if row and row.get("status") else "active").upper()
    tk.Label(win, text=f"Role: {role_text}   •   Status: {status_text}", fg=t["lbl_sub"], bg=t["bg"], font=FONTS["small"]).pack(pady=(0, 8))
    status_lbl = status_label(win, t)

    fields = ["full_name", "phone", "gender", "dob", "bio"]
    v = {k: tk.StringVar(value=str(row[k]) if row and k in row and row[k] else "") for k in fields}
    current_profile_pic = row["profile_pic"] if row and "profile_pic" in row else None

    notebook = ttk.Notebook(win)
    notebook.pack(fill="both", expand=True, padx=12, pady=(6, 0))

    profile_tab = tk.Frame(win, bg=t["bg"])
    photo_tab = tk.Frame(win, bg=t["bg"])
    notebook.add(profile_tab, text="Profile")
    notebook.add(photo_tab, text="Photo")

    # ── Profile tab ───────────────────────────────────────────────────────────
    can_change_role = (row and (row.get("role") in ("admin", "super_admin") or (row.get("role") or "").lower() == "super_admin")) or False
    if can_change_role:
        current_role = normalize_role(row.get("role") or "client")
        role_var = tk.StringVar(value=get_role_label(current_role))
        tk.Label(profile_tab, text="ACCOUNT ROLE", fg=t["lbl_sub"], bg=t["bg"], font=FONTS["label"]).pack(fill="x", padx=40, pady=(10, 2))
        role_display_values = [label for label in USER_ROLES.values()]
        role_combo = ttk.Combobox(profile_tab, textvariable=role_var, values=role_display_values, state="readonly", font=FONTS["body"])
        role_combo.pack(fill="x", padx=40, ipady=4)
    else:
        role_var = None

    for label_text, key in [
        ("FULL NAME", "full_name"),
        ("PHONE NUMBER", "phone"),
        ("GENDER", "gender"),
        ("DATE OF BIRTH (YYYY-MM-DD)", "dob"),
        ("BIOGRAPHY SUMMARY", "bio"),
    ]:
        tk.Label(profile_tab, text=label_text, fg=t["lbl_sub"], bg=t["bg"], font=FONTS["label"]).pack(fill="x", padx=40, pady=(10, 2))
        entry = tk.Entry(profile_tab, textvariable=v[key], font=FONTS["body"], bg=t["input_bg"], fg=t["fg"], bd=0)
        entry.pack(fill="x", padx=40, ipady=5)

    def _save_profile():
        status_lbl.config(text="", fg=t["error"])

        phone_input = v["phone"].get().strip()
        if phone_input.startswith("+256 +256"):
            phone_input = phone_input.replace("+256 +256", "+256")

        try:
            with get_connection() as conn:
                updates = [
                    ("full_name", v["full_name"].get().strip()),
                    ("phone", phone_input),
                    ("gender", v["gender"].get().strip()),
                    ("dob", v["dob"].get().strip()),
                    ("bio", v["bio"].get().strip()),
                ]
                if role_var is not None:
                    updates.append(("role", role_var.get().strip()))

                sql = "UPDATE users SET " + ", ".join(f"{field}= ?" for field, _ in updates) + ", updated_at=CURRENT_TIMESTAMP WHERE id=?"
                values = [value for _, value in updates] + [user_id]
                conn.execute(sql, values)
                conn.commit()

            status_lbl.config(fg=t["success"], text="Profile changes successfully synchronized.")
            if on_save_callback:
                on_save_callback()

        except sqlite3.IntegrityError as e:
            if "users.phone" in str(e):
                status_lbl.config(text="Error: This phone number is already linked to another account.")
            else:
                status_lbl.config(text="Error: Data conflict constraint broken.")

    tk.Button(profile_tab, text="Save Changes", command=_save_profile,
              bg=t["accent"], fg="white", font=FONTS["body_bold"],
              bd=0, cursor="hand2").pack(fill="x", padx=40, pady=(18, 6), ipady=5)

    # ── Photo tab ────────────────────────────────────────────────────────────
    selected_photo = {"path": None}
    preview_label = tk.Label(photo_tab, bg=t["bg"])
    preview_label.pack(pady=(18, 8))

    if current_profile_pic:
        try:
            preview_img = get_circular_avatar(current_profile_pic, (120, 120), t["panel"])
            preview_label.config(image=preview_img)
            preview_label.image = preview_img
        except Exception:
            preview_label.config(text="No profile image yet")

    tk.Label(photo_tab, text="Upload a profile picture for your account.",
             fg=t["lbl_sub"], bg=t["bg"], font=FONTS["small"]).pack(pady=(0, 8))

    def _pick_photo():
        file_path = filedialog.askopenfilename(
            title="Choose profile picture",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")],
        )
        if not file_path:
            return

        project_root = Path(__file__).resolve().parent.parent
        upload_dir = project_root / "assets" / "profile_pics"
        upload_dir.mkdir(exist_ok=True)

        suffix = Path(file_path).suffix.lower() or ".png"
        target_path = upload_dir / f"user_{user_id}_{Path(file_path).stem}{suffix}"

        try:
            with Image.open(file_path) as img:
                img = img.convert("RGBA") if img.mode in ("RGBA", "LA") else img.convert("RGB")
                img = ImageOps.fit(img, (220, 220), Image.Resampling.LANCZOS)
                img.save(target_path)

            selected_photo["path"] = os.path.relpath(target_path, project_root).replace("\\", "/")
            status_lbl.config(fg=t["success"], text="Profile image selected. Click Save Photo to apply it.")

            avatar_img = get_circular_avatar(str(target_path), (120, 120), t["panel"])
            preview_label.config(image=avatar_img)
            preview_label.image = avatar_img
        except Exception as exc:
            status_lbl.config(fg=t["error"], text=f"Unable to use that image: {exc}")

    def _save_photo():
        status_lbl.config(text="", fg=t["error"])
        if not selected_photo["path"]:
            status_lbl.config(fg=t["error"], text="Choose a profile image first.")
            return

        try:
            with get_connection() as conn:
                conn.execute(
                    "UPDATE users SET profile_pic=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                    (selected_photo["path"], user_id),
                )
                conn.commit()
            status_lbl.config(fg=t["success"], text="Profile picture updated successfully.")
            if on_save_callback:
                on_save_callback()
        except sqlite3.IntegrityError:
            status_lbl.config(fg=t["error"], text="Could not update the profile photo.")

    tk.Button(photo_tab, text="Choose Image", command=_pick_photo,
              bg=t["accent"], fg="white", font=FONTS["body_bold"],
              bd=0, cursor="hand2").pack(fill="x", padx=40, pady=(10, 8), ipady=5)
    tk.Button(photo_tab, text="Save Photo", command=_save_photo,
              bg=t["success"], fg="white", font=FONTS["body_bold"],
              bd=0, cursor="hand2").pack(fill="x", padx=40, ipady=5)

    tk.Button(win, text="Discard", command=win.destroy,
              bg=t["btn_sec"], fg=t["btn_sec_fg"],
              font=FONTS["body"], bd=0, cursor="hand2").pack(fill="x", padx=40, pady=(10, 12), ipady=4)