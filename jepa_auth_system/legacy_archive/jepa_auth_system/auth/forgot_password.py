"""
auth/forgot_password.py — Password recovery via security question or recovery code.
"""
import tkinter as tk
from database.db import get_connection
from auth.security import verify_answer, hash_password
from auth.validators import is_strong_password, PASSWORD_HINT
from ui.themes import FONTS
from ui.components import form_label, form_entry, password_entry, action_button, status_label
from utils.logger import log_activity


def open_forgot_password(parent_root: tk.Tk):
    parent_root.withdraw()

    win = tk.Toplevel()
    win.title("Recover Account — JEPA")
    win.geometry("420x560")
    win.resizable(False, False)

    t = {"bg": "#0F172A", "panel": "#1E293B", "fg": "#F8FAFC",
         "lbl_sub": "#94A3B8", "input_bg": "#334155",
         "accent": "#0EA5E9", "accent_hover": "#38BDF8",
         "success": "#10B981", "error": "#EF4444",
         "btn_sec": "#1E293B", "btn_sec_fg": "#94A3B8"}

    win.configure(bg=t["bg"])

    tk.Label(win, text="JEPA WORKSPACE",
             fg=t["accent"], bg=t["bg"], font=FONTS["brand"]).pack(pady=(25, 2))
    tk.Label(win, text="Account Recovery",
             fg=t["fg"], bg=t["bg"], font=FONTS["h1"]).pack(pady=(0, 10))

    status_lbl = status_label(win, t)

    # ── Step state ─────────────────────────────────────────────────────────────
    step = {"current": 1}  # 1 = lookup, 2 = verify, 3 = reset
    found_user = {"row": None}

    v = {k: tk.StringVar() for k in
         ["identifier", "method", "answer", "recovery_code",
          "new_password", "confirm_password"]}
    v["method"].set("question")

    # ── Step 1: Identify account ───────────────────────────────────────────────
    step1_frame = tk.Frame(win, bg=t["bg"])
    step1_frame.pack(fill="x")

    tk.Label(step1_frame, text="ENTER YOUR USERNAME, EMAIL, OR PHONE",
             fg=t["lbl_sub"], bg=t["bg"], font=FONTS["label"]).pack(
        fill="x", padx=45, pady=(10, 2))
    tk.Entry(step1_frame, textvariable=v["identifier"],
             font=FONTS["body"], bg=t["input_bg"], fg=t["fg"],
             insertbackground=t["fg"], bd=0
             ).pack(fill="x", padx=45, ipady=5)

    tk.Label(step1_frame, text="RECOVERY METHOD",
             fg=t["lbl_sub"], bg=t["bg"], font=FONTS["label"]).pack(
        fill="x", padx=45, pady=(10, 2))
    method_frame = tk.Frame(step1_frame, bg=t["bg"])
    method_frame.pack(padx=45, anchor="w")
    for val, txt in [("question", "Security Question"), ("code", "Recovery Code")]:
        tk.Radiobutton(method_frame, text=txt, variable=v["method"], value=val,
                       bg=t["bg"], fg=t["fg"], selectcolor=t["input_bg"],
                       activebackground=t["bg"], font=FONTS["body"]
                       ).pack(side="left", padx=(0, 15))

    def _lookup():
        identifier = v["identifier"].get().strip()
        if not identifier:
            status_lbl.config(text="Please enter your username, email, or phone.")
            return

        with get_connection() as conn:
            row = conn.execute(
                """SELECT id, username, security_question, security_answer_hash, recovery_code
                   FROM users
                   WHERE username=? OR email=? OR phone=?""",
                (identifier, identifier, identifier),
            ).fetchone()

        if not row:
            status_lbl.config(text="No account found with those details.")
            return

        found_user["row"] = dict(row)
        status_lbl.config(text="")
        step1_frame.pack_forget()
        _show_step2()

    tk.Button(step1_frame, text="Continue", command=_lookup,
              bg=t["accent"], fg="white", font=FONTS["body_bold"],
              bd=0, cursor="hand2"
              ).pack(fill="x", padx=45, pady=(20, 8), ipady=5)

    # ── Step 2: Verify identity ────────────────────────────────────────────────
    step2_frame = tk.Frame(win, bg=t["bg"])

    def _show_step2():
        step2_frame.pack(fill="x")
        user = found_user["row"]
        method = v["method"].get()

        for widget in step2_frame.winfo_children():
            widget.destroy()

        if method == "question":
            q = user.get("security_question") or "No security question set."
            tk.Label(step2_frame, text="SECURITY QUESTION",
                     fg=t["lbl_sub"], bg=t["bg"], font=FONTS["label"]
                     ).pack(fill="x", padx=45, pady=(10, 2))
            tk.Label(step2_frame, text=q, fg=t["fg"], bg=t["bg"],
                     font=FONTS["small"], wraplength=330
                     ).pack(padx=45, anchor="w")
            tk.Label(step2_frame, text="YOUR ANSWER",
                     fg=t["lbl_sub"], bg=t["bg"], font=FONTS["label"]
                     ).pack(fill="x", padx=45, pady=(10, 2))
            tk.Entry(step2_frame, textvariable=v["answer"],
                     font=FONTS["body"], bg=t["input_bg"], fg=t["fg"],
                     insertbackground=t["fg"], bd=0
                     ).pack(fill="x", padx=45, ipady=5)
        else:
            tk.Label(step2_frame, text="RECOVERY CODE",
                     fg=t["lbl_sub"], bg=t["bg"], font=FONTS["label"]
                     ).pack(fill="x", padx=45, pady=(10, 2))
            tk.Entry(step2_frame, textvariable=v["recovery_code"],
                     font=FONTS["body"], bg=t["input_bg"], fg=t["fg"],
                     insertbackground=t["fg"], bd=0
                     ).pack(fill="x", padx=45, ipady=5)

        def _verify():
            user = found_user["row"]
            method = v["method"].get()

            if method == "question":
                answer_hash = user.get("security_answer_hash") or ""
                if not verify_answer(v["answer"].get(), answer_hash):
                    status_lbl.config(text="Incorrect answer. Please try again.")
                    return
            else:
                stored = user.get("recovery_code") or ""
                if v["recovery_code"].get().strip() != stored:
                    status_lbl.config(text="Invalid recovery code.")
                    return

            status_lbl.config(text="")
            step2_frame.pack_forget()
            _show_step3()

        tk.Button(step2_frame, text="Verify Identity", command=_verify,
                  bg=t["accent"], fg="white", font=FONTS["body_bold"],
                  bd=0, cursor="hand2"
                  ).pack(fill="x", padx=45, pady=(20, 8), ipady=5)

    # ── Step 3: Set new password ───────────────────────────────────────────────
    step3_frame = tk.Frame(win, bg=t["bg"])

    def _show_step3():
        step3_frame.pack(fill="x")

        tk.Label(step3_frame, text="NEW PASSWORD",
                 fg=t["lbl_sub"], bg=t["bg"], font=FONTS["label"]
                 ).pack(fill="x", padx=45, pady=(10, 2))
        password_entry(step3_frame, v["new_password"], t)

        tk.Label(step3_frame, text="CONFIRM NEW PASSWORD",
                 fg=t["lbl_sub"], bg=t["bg"], font=FONTS["label"]
                 ).pack(fill="x", padx=45, pady=(10, 2))
        password_entry(step3_frame, v["confirm_password"], t)

        def _reset():
            pw = v["new_password"].get()
            if not is_strong_password(pw):
                status_lbl.config(text=PASSWORD_HINT)
                return
            if pw != v["confirm_password"].get():
                status_lbl.config(text="Passwords do not match.")
                return

            user = found_user["row"]
            with get_connection() as conn:
                conn.execute(
                    "UPDATE users SET password_hash=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                    (hash_password(pw), user["id"]),
                )
                conn.commit()

            log_activity("Password Reset", user_id=user["id"],
                         username=user["username"])

            status_lbl.config(fg=t["success"],
                              text="Password updated. Return to sign in.")
            step3_frame.pack_forget()
            tk.Button(win, text="← Back to Sign In", command=_back,
                      bg=t["btn_sec"] if hasattr(t, "btn_sec") else t["input_bg"],
                      fg=t["lbl_sub"], font=FONTS["body_bold"], bd=0
                      ).pack(fill="x", padx=45, pady=(12, 0), ipady=5)

        tk.Button(step3_frame, text="Reset Password", command=_reset,
                  bg=t["success"], fg="white", font=FONTS["body_bold"],
                  bd=0, cursor="hand2"
                  ).pack(fill="x", padx=45, pady=(20, 8), ipady=5)

    def _back():
        win.destroy()
        parent_root.deiconify()

    win.protocol("WM_DELETE_WINDOW", _back)
    win.mainloop()
