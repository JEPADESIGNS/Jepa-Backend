"""Basic task management view for JEPA Site Manager."""

import tkinter as tk
from tkinter import ttk

from ui.themes import FONTS
from jepa_site_manager.tasks.task_service import create_task, list_tasks


def open_task_view(parent: tk.Misc, user_id: int | None = None, default_project_id: int | None = None) -> None:
    """Open a simple task management window."""
    win = tk.Toplevel(parent)
    win.title("JEPA Site Manager — Tasks")
    win.geometry("900x520")
    win.configure(bg="#0F172A")

    tk.Label(win, text="TASK MANAGEMENT", fg="#0EA5E9", bg="#0F172A", font=FONTS["h2"]).pack(pady=(18, 6))
    tk.Label(win, text="Create and review project tasks for daily operations.", fg="#94A3B8", bg="#0F172A", font=FONTS["small"]).pack()

    form = tk.Frame(win, bg="#0F172A")
    form.pack(fill="x", padx=18, pady=10)

    filter_label = tk.Label(win, text="Showing all tasks" if default_project_id is None else f"Showing tasks for project {default_project_id}", fg="#E2E8F0", bg="#0F172A", font=FONTS["small"])
    filter_label.pack(anchor="w", padx=18)

    fields = {
        "project_id": tk.StringVar(value=str(default_project_id) if default_project_id is not None else ""),
        "site_id": tk.StringVar(),
        "title": tk.StringVar(),
        "status": tk.StringVar(value="Planned"),
        "progress_percent": tk.StringVar(value="0"),
    }

    for label, var in [
        ("Project ID", fields["project_id"]),
        ("Site ID", fields["site_id"]),
        ("Task Title", fields["title"]),
        ("Status", fields["status"]),
        ("Progress %", fields["progress_percent"]),
    ]:
        row = tk.Frame(form, bg="#0F172A")
        row.pack(fill="x", pady=3)
        tk.Label(row, text=label, fg="#94A3B8", bg="#0F172A", font=FONTS["label"]).pack(side="left", anchor="w")
        tk.Entry(row, textvariable=var, bg="#334155", fg="#F8FAFC", bd=0, insertbackground="#F8FAFC", font=FONTS["body"]).pack(side="left", fill="x", expand=True)

    def _save() -> None:
        try:
            project_id = int(fields["project_id"].get().strip())
            site_id = int(fields["site_id"].get().strip()) if fields["site_id"].get().strip() else None
            progress_percent = int(fields["progress_percent"].get().strip() or 0)
        except ValueError:
            tk.messagebox.showwarning("Required", "Project ID, Site ID, and Progress must be numeric.")
            return

        task_id = create_task(
            project_id=project_id,
            site_id=site_id,
            title=fields["title"].get().strip(),
            status=fields["status"].get().strip() or "Planned",
            progress_percent=progress_percent,
            assigned_user_id=user_id,
        )
        tk.messagebox.showinfo("Saved", f"Task created with id {task_id}.")
        _refresh()

    tk.Button(form, text="Save Task", command=_save, bg="#0EA5E9", fg="white", font=FONTS["body_bold"], bd=0, cursor="hand2").pack(pady=(10, 0), ipady=4)

    tree = ttk.Treeview(win, columns=("id", "project_id", "site_id", "title", "status", "progress"), show="headings")
    tree.heading("id", text="ID")
    tree.heading("project_id", text="Project ID")
    tree.heading("site_id", text="Site ID")
    tree.heading("title", text="Task")
    tree.heading("status", text="Status")
    tree.heading("progress", text="Progress %")
    tree.pack(fill="both", expand=True, padx=18, pady=(10, 18))

    def _refresh() -> None:
        for item in tree.get_children():
            tree.delete(item)
        rows = list_tasks(default_project_id) if default_project_id is not None else list_tasks()
        for row in rows:
            tree.insert("", "end", values=(row["id"], row["project_id"], row["site_id"] or "", row["title"], row["status"], row["progress_percent"]))

    _refresh()
