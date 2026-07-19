"""Issue tracking workspace for JEPA Site Manager."""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime

from ui.themes import FONTS

from jepa_site_manager.projects.project_service import list_projects
from jepa_site_manager.issues.issue_service import (
    list_issues,
    create_issue,
    update_issue,
    delete_issue,
    get_issue,
)

# testing hook - last opened form window
last_issue_form: tk.Toplevel | None = None


def open_issue_view(parent: tk.Misc, user_id: int | None = None) -> None:
    win = tk.Toplevel(parent)
    win.title("JEPA Site Manager — Issues")
    win.geometry("980x520")
    win.configure(bg="#0F172A")

    tk.Label(win, text="ISSUES & OBSERVATIONS", fg="#0EA5E9", bg="#0F172A", font=FONTS["h2"]).pack(pady=(12, 6))
    tk.Label(win, text="Create, edit and resolve issues linked to projects.", fg="#94A3B8", bg="#0F172A", font=FONTS["small"]).pack()

    container = tk.Frame(win, bg="#0F172A")
    container.pack(fill="both", expand=True, padx=12, pady=12)

    left = tk.Frame(container, bg="#0F172A", width=320)
    left.pack(side="left", fill="y")
    left.pack_propagate(False)

    right = tk.Frame(container, bg="#0F172A")
    right.pack(side="left", fill="both", expand=True, padx=(12, 0))

    # Project selector
    tk.Label(left, text="Project", fg="#CBD5E1", bg="#0F172A", font=FONTS["label"]).pack(anchor="w", pady=(6, 0))
    project_var = tk.StringVar()
    project_combo = ttk.Combobox(left, textvariable=project_var, state="readonly", font=FONTS["body"])
    project_combo.pack(fill="x")

    projects = list_projects()
    project_map = {f"{p['id']}: {p['project_name']}": p["id"] for p in projects}
    project_combo['values'] = list(project_map.keys())
    if project_combo['values']:
        project_combo.current(0)

    # Treeview for issues
    cols = ("id", "title", "priority", "status", "assigned_to_id", "created_at")
    tree = ttk.Treeview(right, columns=cols, show='headings', selectmode='browse')
    for c in cols:
        tree.heading(c, text=c.replace('_', ' ').title())
        tree.column(c, width=120 if c != 'title' else 280)
    tree.pack(fill="both", expand=True)

    # Buttons
    btn_frame = tk.Frame(left, bg="#0F172A")
    btn_frame.pack(fill="x", pady=(12, 0))

    def refresh():
        tree.delete(*tree.get_children())
        sel = project_var.get()
        if not sel:
            return
        pid = project_map.get(sel)
        try:
            rows = list_issues(pid)
        except Exception:
            rows = []
        if not rows:
            # show empty state
            pass
        for r in rows:
            tree.insert('', 'end', values=(r['id'], r['title'], r['priority'], r['status'], r.get('assigned_to_id'), r['created_at']))

    def _open_form(existing: dict | None = None):
        print('DEBUG: _open_form called, existing=', bool(existing))
        top = tk.Toplevel(win)
        global last_issue_form
        last_issue_form = top
        top.title("Issue")
        top.geometry("520x420")
        top.configure(bg="#0F172A")

        fields = {
            'title': tk.StringVar(value=(existing['title'] if existing else '')),
            'description': tk.StringVar(value=(existing['description'] if existing else '')),
            'priority': tk.StringVar(value=(existing['priority'] if existing else 'Medium')),
            'status': tk.StringVar(value=(existing['status'] if existing else 'Open')),
        }

        tk.Label(top, text="Title", fg="#CBD5E1", bg="#0F172A", font=FONTS['label']).pack(anchor='w', padx=12, pady=(12,0))
        tk.Entry(top, textvariable=fields['title'], font=FONTS['body']).pack(fill='x', padx=12)

        tk.Label(top, text="Description", fg="#CBD5E1", bg="#0F172A", font=FONTS['label']).pack(anchor='w', padx=12, pady=(8,0))
        tk.Entry(top, textvariable=fields['description'], font=FONTS['body']).pack(fill='x', padx=12)

        tk.Label(top, text="Priority", fg="#CBD5E1", bg="#0F172A", font=FONTS['label']).pack(anchor='w', padx=12, pady=(8,0))
        ttk.Combobox(top, textvariable=fields['priority'], values=["Low", "Medium", "High"], state='readonly').pack(fill='x', padx=12)

        tk.Label(top, text="Status", fg="#CBD5E1", bg="#0F172A", font=FONTS['label']).pack(anchor='w', padx=12, pady=(8,0))
        ttk.Combobox(top, textvariable=fields['status'], values=["Open", "In Progress", "Resolved"], state='readonly').pack(fill='x', padx=12)

        def _save():
            sel = project_var.get()
            if not sel:
                messagebox.showwarning("Select project", "Please select a project first.")
                return
            pid = project_map.get(sel)
            title = fields['title'].get().strip()
            if not title:
                messagebox.showwarning("Required", "Title is required")
                return
            if existing:
                update_issue(existing['id'], title=title, description=fields['description'].get(), priority=fields['priority'].get(), status=fields['status'].get(), updated_by=None)
            else:
                create_issue(pid, title, description=fields['description'].get(), priority=fields['priority'].get(), created_by=None, status=fields['status'].get())
            top.destroy()
            refresh()

        tk.Button(top, text="Save", command=_save, bg="#0EA5E9", fg='white', font=FONTS['body_bold']).pack(pady=12)

    def on_create():
        _open_form(None)

    def on_edit():
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select an issue to edit")
            return
        values = tree.item(sel[0], 'values')
        issue = get_issue(int(values[0]))
        if issue:
            _open_form(issue)

    def on_delete():
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select an issue to delete")
            return
        values = tree.item(sel[0], 'values')
        iid = int(values[0])
        if messagebox.askyesno("Confirm", "Delete selected issue?"):
            delete_issue(iid, deleted_by=None)
            refresh()

    tk.Button(btn_frame, text="New Issue", command=on_create, bg="#06B6D4", fg='white', font=FONTS['body']).pack(fill='x', pady=4)
    tk.Button(btn_frame, text="Edit Issue", command=on_edit, bg="#0EA5E9", fg='white', font=FONTS['body']).pack(fill='x', pady=4)
    tk.Button(btn_frame, text="Delete Issue", command=on_delete, bg="#F43F5E", fg='white', font=FONTS['body']).pack(fill='x', pady=4)

    # Initial load
    refresh()
