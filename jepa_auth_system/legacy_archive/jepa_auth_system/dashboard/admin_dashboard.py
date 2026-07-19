"""
dashboard/admin_dashboard.py — Admin management panel with user controls and 2FA resets.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from database.db import get_connection
from ui.themes import FONTS, get_theme
from ui.components import resolve_asset
from utils.logger import log_activity
from utils.csv_export import export_users_to_csv


def admin_dashboard(user_id: int, username: str, saved_theme: str = "dark"):
    dash = tk.Tk()
    dash.title("Administrative Suite — JEPA")
    dash.geometry("1120x680")
    dash.configure(bg="#0F172A")

    try:
        dash.iconbitmap(str(resolve_asset("app_icon.ico")))
    except Exception:
        pass

    # ── Treeview style ─────────────────────────────────────────────────────────
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Admin.Treeview",
                    background="#1E293B",
                    fieldbackground="#1E293B",
                    foreground="#F8FAFC",
                    rowheight=28)
    style.configure("Admin.Treeview.Heading",
                    background="#334155",
                    foreground="#F8FAFC",
                    font=FONTS["label"])
    style.map("Admin.Treeview", background=[("selected", "#0EA5E9")])

    # ── Header ─────────────────────────────────────────────────────────────────
    hdr = tk.Frame(dash, bg="#0F172A")
    hdr.pack(fill="x", padx=25, pady=(20, 10))

    tk.Label(hdr, text="ADMIN MANAGEMENT CONSOLE", font=FONTS["brand"],
             fg="#0EA5E9", bg="#0F172A").pack(side="left")

    lbl_admin = tk.Label(hdr, text=f"Admin: {username.upper()} (ID: #{user_id})",
                         font=FONTS["small_bold"], fg="#94A3B8", bg="#0F172A")
    lbl_admin.pack(side="right", pady=5)

    # ── Main Table Frame ──────────────────────────────────────────────────────
    tree_frame = tk.Frame(dash, bg="#0F172A")
    tree_frame.pack(padx=25, pady=10, fill="both", expand=True)

    columns = ("id", "username", "email", "phone", "full_name", "role", "status", "2fa_status")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", style="Admin.Treeview")
    
    # Define Headings
    tree.heading("id", text="ID")
    tree.heading("username", text="USERNAME")
    tree.heading("email", text="EMAIL ADDRESS")
    tree.heading("phone", text="PHONE")
    tree.heading("full_name", text="FULL NAME")
    tree.heading("role", text="ROLE")
    tree.heading("status", text="STATUS")
    tree.heading("2fa_status", text="2FA AUTH")

    # Define Column Widths
    tree.column("id", width=50, anchor="center")
    tree.column("username", width=120, anchor="w")
    tree.column("email", width=180, anchor="w")
    tree.column("phone", width=130, anchor="w")
    tree.column("full_name", width=150, anchor="w")
    tree.column("role", width=80, anchor="center")
    tree.column("status", width=90, anchor="center")
    tree.column("2fa_status", width=90, anchor="center")

    sb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")

    def _load():
        """Fetch all database records and refresh rows inside the UI view."""
        for item in tree.get_children():
            tree.delete(item)

        with get_connection() as conn:
            rows = conn.execute(
                """SELECT id, username, email, phone, full_name, role, status, totp_secret 
                   FROM users ORDER BY id ASC"""
            ).fetchall()

        for r in rows:
            two_factor = "Enabled" if r["totp_secret"] else "Disabled"
            tree.insert("", "end", values=(
                r["id"], r["username"], r["email"] or "N/A", r["phone"] or "N/A",
                r["full_name"] or "N/A", r["role"].upper(), r["status"].upper(), two_factor
            ))

    def _get_selected():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please choose a user target from the panel table.")
            return None
        return tree.item(sel[0])["values"]

    # ── Admin Action Operations ────────────────────────────────────────────────
    def _toggle_status():
        target = _get_selected()
        if not target: return
        target_id, target_user, current_status = target[0], target[1], target[6].lower()

        if target_id == user_id:
            messagebox.showerror("Action Denied", "Security policy prevents self-suspension rules.")
            return

        new_status = "active" if current_status == "suspended" else "suspended"
        
        with get_connection() as conn:
            conn.execute("UPDATE users SET status=? WHERE id=?", (new_status, target_id))
            conn.commit()

        log_activity(f"User {new_status.capitalize()}", user_id=user_id, username=username, details=f"Target: {target_user}")
        _load()

    def _reset_password():
        target = _get_selected()
        if not target: return
        target_id, target_user = target[0], target[1]

        from auth.security import hash_password
        default_pw = "Reset@2026!"
        hashed = hash_password(default_pw)

        with get_connection() as conn:
            conn.execute("UPDATE users SET password_hash=? WHERE id=?", (hashed, target_id))
            conn.commit()

        log_activity("Password Reset By Admin", user_id=user_id, username=username, details=f"Target: {target_user}")
        messagebox.showinfo("Password Reset", f"Temporary credentials for '{target_user}' set to:\n\n{default_pw}")

    def _promote_to_admin():
        target = _get_selected()
        if not target: return
        target_id, target_user = target[0], target[1]

        with get_connection() as conn:
            conn.execute("UPDATE users SET role='admin' WHERE id=?", (target_id,))
            conn.commit()

        log_activity("User Promoted", user_id=user_id, username=username, details=f"Target: {target_user}")
        _load()

    def _reset_2fa():
        """Clears out the user's totp_secret, disabling 2FA verification."""
        target = _get_selected()
        if not target: return
        target_id, target_user, has_2fa = target[0], target[1], target[7]

        if has_2fa == "Disabled":
            messagebox.showinfo("Info", f"Two-Factor protection is already inactive for '{target_user}'.")
            return

        confirm = messagebox.askyesno("Confirm 2FA Reset", f"Are you sure you want to completely disable and remove 2FA access tokens for '{target_user}'?")
        if not confirm:
            return

        with get_connection() as conn:
            conn.execute("UPDATE users SET totp_secret=NULL WHERE id=?", (target_id,))
            conn.commit()

        log_activity("2FA Disabled By Admin", user_id=user_id, username=username, details=f"Target: {target_user}")
        messagebox.showinfo("Success", f"Two-Factor Authentication configuration wiped for account '{target_user}'.")
        _load()

    def _export_csv():
        try:
            path = export_users_to_csv()
            messagebox.showinfo("Export Successful", f"Account structural backup tables saved to Desktop:\n{path.name}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Unable to parse database file system mappings: {e}")

    def _logout():
        log_activity("Logout", user_id=user_id, username=username)
        dash.destroy()
        from auth.login import login_window
        login_window()

    # ── Action Control Grid ────────────────────────────────────────────────────
    action_bar = tk.Frame(dash, bg="#0F172A")
    action_bar.pack(padx=25, pady=(8, 16), fill="x")

    btn_cfg = dict(bd=0, cursor="hand2", font=FONTS["small_bold"], padx=12, pady=4)

    tk.Button(action_bar, text="↻  Refresh", command=_load, bg="#334155", fg="#F8FAFC", **btn_cfg).pack(side="left", padx=(0, 6))
    tk.Button(action_bar, text="⊘  Suspend / Reinstate", command=_toggle_status, bg="#F59E0B", fg="white", **btn_cfg).pack(side="left", padx=(0, 6))
    tk.Button(action_bar, text="🔑  Reset Password", command=_reset_password, bg="#6366F1", fg="white", **btn_cfg).pack(side="left", padx=(0, 6))
    tk.Button(action_bar, text="🛡️  Reset 2FA", command=_reset_2fa, bg="#EC4899", fg="white", **btn_cfg).pack(side="left", padx=(0, 6))
    tk.Button(action_bar, text="⬆  Promote to Admin", command=_promote_to_admin, bg="#10B981", fg="white", **btn_cfg).pack(side="left", padx=(0, 6))
    tk.Button(action_bar, text="📥  Export CSV Mappings", command=_export_csv, bg="#0EA5E9", fg="white", **btn_cfg).pack(side="left", padx=(0, 6))
    tk.Button(action_bar, text="🚪  Log Out", command=_logout, bg="#EF4444", fg="white", **btn_cfg).pack(side="right")

    _load()
    dash.mainloop()