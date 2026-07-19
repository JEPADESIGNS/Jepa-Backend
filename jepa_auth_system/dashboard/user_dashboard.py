"""
dashboard/user_dashboard.py — User account dashboard with theme switching and 2FA configuration.
"""
import tkinter as tk
from tkinter import ttk
import qrcode
from PIL import Image, ImageTk

from database.db import get_connection
from ui.themes import get_theme, FONTS
from ui.components import get_circular_avatar, resolve_asset, status_label
from utils.logger import log_activity
from auth.security import generate_totp_secret, get_totp_uri, verify_totp
from dashboard import get_accessible_site_manager_actions, get_role_label, open_site_manager_module


def user_dashboard(user_id: int, username: str, saved_theme: str = "dark"):
    t = get_theme(saved_theme)

    dash = tk.Tk()
    dash.title("JEPA Site Manager — User Workspace")
    dash.geometry("480x760")
    dash.resizable(True, True)
    dash.configure(bg=t["bg"])

    try:
        dash.iconbitmap(str(resolve_asset("app_icon.ico")))
    except Exception:
        pass

    state = {"theme": saved_theme, "data": {}}

    def _load_data():
        with get_connection() as conn:
            row = conn.execute(
                """SELECT profile_pic, full_name, country_code, phone,
                          gender, dob, bio, theme, email, totp_secret, role, status
                   FROM users WHERE id=?""",
                (user_id,),
            ).fetchone()
        if row:
            state["data"] = dict(row)
            state["theme"] = row["theme"] or "dark"

    def _apply_theme():
        t = get_theme(state["theme"])
        dash.configure(bg=t["bg"])
        card_frame.config(bg=t["panel"], highlightbackground=t["border"])
        hdr_frame.config(bg=t["panel2"])
        hdr_lbl.config(bg=t["panel2"], fg=t["fg"])
        role_badge.config(bg=t["panel2"], fg=t["accent_hover"])
        theme_btn.config(bg=t["btn_sec"], fg=t["btn_sec_fg"], 
                         text="☀️ Light Mode" if state["theme"] == "dark" else "🌙 Dark Mode")
        
        # Dynamic label updates
        data = state["data"]
        lbl_name.config(text=(data["full_name"] or username).upper(), fg=t["fg"], bg=t["panel"])
        lbl_role.config(text=f"ID: #{user_id}  |  {data['email'] or 'No Email'}", fg=t["lbl_sub"], bg=t["panel"])
        role_badge.config(text=f"Role: {get_role_label(data.get('role'))}  •  Status: {(data.get('status') or 'active').upper()}", fg="#38BDF8", bg="#0F172A")
        
        phone_val = f"{data['country_code'] or ''} {data['phone'] or ''}".strip()
        lbl_phone.config(text=f"📞  {phone_val or 'No phone linked'}", fg=t["fg"], bg=t["panel"])
        lbl_demo.config(text=f"🧬  {data['gender'] or 'Not specified'}   •   🎂  {data['dob'] or 'No DOB'}", fg=t["fg"], bg=t["panel"])
        lbl_bio.config(text=data["bio"] or "No bio written yet.", fg=t["lbl_sub"], bg=t["panel"])

        # Update Avatar
        try:
            img = get_circular_avatar(data["profile_pic"], (110, 110), t["panel"])
            lbl_avatar.config(image=img)
            lbl_avatar.image = img
        except Exception:
            pass

    _load_data()

    # ── Header ─────────────────────────────────────────────────────────────────
    hdr_frame = tk.Frame(dash, bg=get_theme(saved_theme)["panel2"])
    hdr_frame.pack(fill="x", padx=30, pady=(20, 10))
    hdr_lbl = tk.Label(hdr_frame, text="JEPA SITE MANAGER", font=FONTS["brand"])
    hdr_lbl.pack(side="left")

    tk.Label(hdr_frame, text="PROJECT OPERATIONS", fg="#06B6D4", bg=get_theme(saved_theme)["panel2"], font=FONTS["small_bold"]).pack(side="left", padx=(10, 0))

    role_badge = tk.Label(hdr_frame, text="Current Project • On Track • 68% progress", fg="#F0A500", bg=get_theme(saved_theme)["panel2"], font=FONTS["small_bold"])
    role_badge.pack(side="left", padx=(12, 0))

    def _toggle_theme():
        next_theme = "light" if state["theme"] == "dark" else "dark"
        with get_connection() as conn:
            conn.execute("UPDATE users SET theme=? WHERE id=?", (next_theme, user_id))
            conn.commit()
        state["theme"] = next_theme
        _apply_theme()

    theme_btn = tk.Button(hdr_frame, bd=0, cursor="hand2", font=FONTS["small_bold"], command=_toggle_theme)
    theme_btn.pack(side="right", ipady=2, padx=2)

    # ── Profile Card ───────────────────────────────────────────────────────────
    card_frame = tk.Frame(dash, bg=t["panel"], highlightthickness=1, highlightbackground=t["border"], bd=0)
    card_frame.pack(padx=30, pady=10, fill="x")

    lbl_avatar = tk.Label(card_frame, bd=0)
    lbl_avatar.pack(pady=(25, 10))

    lbl_name = tk.Label(card_frame, font=FONTS["h2"])
    lbl_name.pack()

    lbl_role = tk.Label(card_frame, font=FONTS["small"])
    lbl_role.pack(pady=(2, 15))

    def _section(title):
        tk.Label(card_frame, text=title, font=FONTS["label"], fg="#F0A500", bg=card_frame["bg"]).pack(pady=(10, 2))
        lbl = tk.Label(card_frame, font=FONTS["body"])
        lbl.pack(pady=(0, 10))
        return lbl

    lbl_phone = _section("PROJECT LOCATION")
    lbl_demo  = _section("SITE STATUS")
    lbl_bio   = _section("TODAY'S SITE SUMMARY")
    lbl_bio.config(font=FONTS["small"], wraplength=330, justify="center")

    # ── Action Buttons ─────────────────────────────────────────────────────────
    def _edit_profile():
        from dashboard.profile import open_profile_editor
        open_profile_editor(
            dash, user_id, username, get_theme(state["theme"]),
            on_save_callback=lambda: (_load_data(), _apply_theme()))

    def _change_password():
        from dashboard.change_password import open_change_password
        open_change_password(dash, user_id, username, get_theme(state["theme"]))

    def _logout():
        log_activity("Logout", user_id=user_id, username=username)
        dash.destroy()
        from auth.login import login_window
        login_window()

    btn_cfg = dict(bd=0, cursor="hand2", font=FONTS["body_bold"])

    tk.Button(
        dash,
        text="🏢  JEPA Site Manager Hub",
        command=lambda: open_site_manager_module(dash, "overview"),
        bg=t["btn_sec"],
        fg=t["btn_sec_fg"],
        **btn_cfg,
    ).pack(pady=(14, 4), padx=30, fill="x", ipady=4)

    tk.Button(dash, text="✏️  Edit Profile", command=_edit_profile, bg=t["accent"], fg="white", **btn_cfg).pack(pady=(4, 4), padx=30, fill="x", ipady=4)
    tk.Button(dash, text="🔑  Change Password", command=_change_password, bg=t["panel"], fg=t["fg"], **btn_cfg).pack(pady=4, padx=30, fill="x", ipady=4)

    tk.Label(dash, text="SITE OPERATIONS MODULES", fg=t["accent_hover"], bg=t["bg"], font=FONTS["label"]).pack(pady=(10, 6))
    for label, module_name in get_accessible_site_manager_actions(state["data"].get("role")):
        tk.Button(
            dash,
            text=f"📂  {label}",
            command=lambda module_name=module_name: open_site_manager_module(dash, module_name),
            bg=t["panel"],
            fg=t["fg"],
            **btn_cfg,
        ).pack(pady=4, padx=30, fill="x", ipady=4)

    # 2FA SETUP INTERFACE ACTIVATOR
    def _setup_2fa():
        _open_2fa_setup_window(dash, user_id, username, state["data"].get("email"), get_theme(state["theme"]), on_success=_load_data)

    tk.Button(dash, text="🛡️  Setup Two-Factor (2FA)", command=_setup_2fa, bg=t["success"], fg="white", **btn_cfg).pack(pady=4, padx=30, fill="x", ipady=4)
    tk.Button(dash, text="🚪  Log Out", command=_logout, bg="#EF4444", fg="white", **btn_cfg).pack(pady=(4, 20), padx=30, fill="x", ipady=4)

    _apply_theme()
    dash.mainloop()


def _open_2fa_setup_window(parent, user_id, username, email, theme, on_success):
    """Generates a secret key and loads a temporary QR image widget onto the screen."""
    t = theme
    win = tk.Toplevel(parent)
    win.title("2FA Activation Wizard")
    win.geometry("380x520")
    win.resizable(False, False)
    win.configure(bg=t["bg"])
    win.grab_set()

    tk.Label(win, text="Activate 2FA Protection", fg=t["accent"], bg=t["bg"], font=("Segoe UI", 14, "bold")).pack(pady=(20, 5))
    
    # Generate the secret temporary strings
    secret = generate_totp_secret()
    uri = get_totp_uri(email or username, secret)

    # Build QR Code using PIL pipeline
    qr = qrcode.QRCode(box_size=4, border=2)
    qr.add_data(uri)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    qr_img = qr_img.resize((160, 160), Image.Resampling.LANCZOS)
    img_tk = ImageTk.PhotoImage(qr_img)

    qr_label = tk.Label(win, image=img_tk, bd=0)
    qr_label.image = img_tk  # Keep memory references alive
    qr_label.pack(pady=10)

    tk.Label(win, text=f"Secret Key: {secret}", fg=t["lbl_sub"], bg=t["bg"], font=("Consolas", 10, "bold")).pack()
    tk.Label(win, text="Scan with Google Authenticator or Authy,\nthen input the 6-digit verification code below:", 
             fg=t["fg"], bg=t["bg"], font=("Segoe UI", 9), justify="center").pack(pady=(10, 5))

    v_code = tk.StringVar()
    status_lbl = status_label(win, t)

    entry = tk.Entry(win, textvariable=v_code, font=("Consolas", 14), bg=t["input_bg"], fg=t["fg"], justify="center", bd=0)
    entry.pack(fill="x", padx=80, ipady=4, pady=5)

    def _verify_and_save():
        if verify_totp(secret, v_code.get()):
            with get_connection() as conn:
                conn.execute("UPDATE users SET totp_secret=? WHERE id=?", (secret, user_id))
                conn.commit()
            log_activity("2FA Enabled", user_id=user_id, username=username)
            on_success()
            win.destroy()
            from tkinter import messagebox
            messagebox.showinfo("Success", "Two-Factor Authentication is now enabled on your account!")
        else:
            status_lbl.config(text="Invalid verification code. Please check your app.")

    tk.Button(win, text="Verify & Enable", command=_verify_and_save, bg=t["accent"], fg="white", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2").pack(fill="x", padx=80, pady=15, ipady=4)