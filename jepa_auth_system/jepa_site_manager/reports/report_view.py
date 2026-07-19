"""Daily site report view for JEPA Site Manager."""

import tkinter as tk
from tkinter import ttk

from ui.themes import FONTS
from jepa_site_manager.reports.report_service import create_report, list_reports


def open_report_view(parent: tk.Misc, user_id: int | None = None, default_project_id: int | None = None) -> None:
    """Open a basic daily site report entry screen."""
    win = tk.Toplevel(parent)
    win.title("JEPA Site Manager — Reports")
    win.geometry("920x520")
    win.configure(bg="#0F172A")

    tk.Label(win, text="DAILY SITE REPORTS", fg="#0EA5E9", bg="#0F172A", font=FONTS["h2"]).pack(pady=(18, 6))
    tk.Label(win, text="Capture site activity, weather, issues, and workers present.", fg="#94A3B8", bg="#0F172A", font=FONTS["small"]).pack()

    form = tk.Frame(win, bg="#0F172A")
    form.pack(fill="x", padx=18, pady=10)

    fields = {
        "project_id": tk.StringVar(value=str(default_project_id) if default_project_id is not None else ""),
        "report_date": tk.StringVar(value="2026-06-11"),
        "weather": tk.StringVar(),
        "activities": tk.StringVar(),
        "workers_present": tk.StringVar(),
        "issues": tk.StringVar(),
    }

    for label, var in [
        ("Project ID", fields["project_id"]),
        ("Report Date", fields["report_date"]),
        ("Weather", fields["weather"]),
        ("Activities", fields["activities"]),
        ("Workers Present", fields["workers_present"]),
        ("Issues", fields["issues"]),
    ]:
        row = tk.Frame(form, bg="#0F172A")
        row.pack(fill="x", pady=3)
        tk.Label(row, text=label, fg="#94A3B8", bg="#0F172A", font=FONTS["label"]).pack(side="left", anchor="w")
        tk.Entry(row, textvariable=var, bg="#334155", fg="#F8FAFC", bd=0, insertbackground="#F8FAFC", font=FONTS["body"]).pack(side="left", fill="x", expand=True)

    def _save() -> None:
        try:
            project_id = int(fields["project_id"].get().strip())
        except ValueError:
            tk.messagebox.showwarning("Required", "Project ID must be a number.")
            return

        report_id = create_report(
            project_id=project_id,
            report_date=fields["report_date"].get().strip() or "2026-06-11",
            weather=fields["weather"].get().strip(),
            activities=fields["activities"].get().strip(),
            workers_present=fields["workers_present"].get().strip(),
            issues=fields["issues"].get().strip(),
            created_by=user_id,
        )
        tk.messagebox.showinfo("Saved", f"Site report created with id {report_id}.")
        _refresh()

    tk.Button(form, text="Save Daily Report", command=_save, bg="#0EA5E9", fg="white", font=FONTS["body_bold"], bd=0, cursor="hand2").pack(pady=(10, 0), ipady=4)

    tree = ttk.Treeview(win, columns=("id", "project_id", "date", "weather", "workers", "issues"), show="headings")
    tree.heading("id", text="ID")
    tree.heading("project_id", text="Project ID")
    tree.heading("date", text="Date")
    tree.heading("weather", text="Weather")
    tree.heading("workers", text="Workers")
    tree.heading("issues", text="Issues")
    tree.pack(fill="both", expand=True, padx=18, pady=(10, 18))

    def _refresh() -> None:
        for item in tree.get_children():
            tree.delete(item)
        for row in list_reports():
            tree.insert("", "end", values=(row["id"], row["project_id"], row["report_date"], row["weather"] or "", row["workers_present"] or "", row["issues"] or ""))

    _refresh()
