"""Documents workspace for JEPA Site Manager."""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from ui.themes import FONTS

from jepa_site_manager.projects.project_service import list_projects
from jepa_site_manager.documents.document_service import (
    list_documents,
    upload_document,
    get_document,
    delete_document,
    update_document,
)

# testing hook
last_document_form: tk.Toplevel | None = None


def open_document_view(parent: tk.Misc) -> None:
    win = tk.Toplevel(parent)
    win.title("JEPA Site Manager — Documents")
    win.geometry("980x520")
    win.configure(bg="#0F172A")

    tk.Label(win, text="DOCUMENTS & SUBMITTALS", fg="#0EA5E9", bg="#0F172A", font=FONTS["h2"]).pack(pady=(12, 6))
    tk.Label(win, text="Upload and manage project documents.", fg="#94A3B8", bg="#0F172A", font=FONTS["small"]).pack()

    container = tk.Frame(win, bg="#0F172A")
    container.pack(fill="both", expand=True, padx=12, pady=12)

    left = tk.Frame(container, bg="#0F172A", width=320)
    left.pack(side="left", fill="y")
    left.pack_propagate(False)

    right = tk.Frame(container, bg="#0F172A")
    right.pack(side="left", fill="both", expand=True, padx=(12, 0))

    tk.Label(left, text="Project", fg="#CBD5E1", bg="#0F172A", font=FONTS["label"]).pack(anchor="w", pady=(6, 0))
    project_var = tk.StringVar()
    project_combo = ttk.Combobox(left, textvariable=project_var, state="readonly", font=FONTS["body"])
    project_combo.pack(fill="x")

    projects = list_projects()
    project_map = {f"{p['id']}: {p['project_name']}": p['id'] for p in projects}
    project_combo['values'] = list(project_map.keys())
    if project_combo['values']:
        project_combo.current(0)

    cols = ("id", "title", "document_type", "uploaded_by", "uploaded_at")
    tree = ttk.Treeview(right, columns=cols, show='headings', selectmode='browse')
    for c in cols:
        tree.heading(c, text=c.replace('_', ' ').title())
        tree.column(c, width=140 if c!='title' else 300)
    tree.pack(fill='both', expand=True)

    btn_frame = tk.Frame(left, bg="#0F172A")
    btn_frame.pack(fill="x", pady=(12, 0))

    def refresh():
        tree.delete(*tree.get_children())
        sel = project_var.get()
        if not sel:
            return
        pid = project_map.get(sel)
        try:
            rows = list_documents(pid)
        except Exception:
            rows = []
        for r in rows:
            tree.insert('', 'end', values=(r['id'], r['title'], r.get('document_type'), r.get('uploaded_by'), r.get('uploaded_at')))

    def _open_form(existing: dict | None = None):
        top = tk.Toplevel(win)
        global last_document_form
        last_document_form = top
        top.title('Document')
        top.geometry('520x380')
        top.configure(bg="#0F172A")

        fields = {
            'title': tk.StringVar(value=(existing['title'] if existing else '')),
            'document_type': tk.StringVar(value=(existing.get('document_type') if existing else '')),
            'description': tk.StringVar(value=(existing.get('description') if existing else '')),
        }

        tk.Label(top, text='Title', fg="#CBD5E1", bg="#0F172A", font=FONTS['label']).pack(anchor='w', padx=12, pady=(12,0))
        tk.Entry(top, textvariable=fields['title'], font=FONTS['body']).pack(fill='x', padx=12)

        tk.Label(top, text='Type', fg="#CBD5E1", bg="#0F172A", font=FONTS['label']).pack(anchor='w', padx=12, pady=(8,0))
        tk.Entry(top, textvariable=fields['document_type'], font=FONTS['body']).pack(fill='x', padx=12)

        tk.Label(top, text='Description', fg="#CBD5E1", bg="#0F172A", font=FONTS['label']).pack(anchor='w', padx=12, pady=(8,0))
        tk.Entry(top, textvariable=fields['description'], font=FONTS['body']).pack(fill='x', padx=12)

        def _save():
            sel = project_var.get()
            if not sel:
                messagebox.showwarning('Select project', 'Please select a project first.')
                return
            pid = project_map.get(sel)
            title = fields['title'].get().strip()
            if not title:
                messagebox.showwarning('Required', 'Title is required')
                return
            if existing:
                update_document(existing['id'], title=title, document_type=fields['document_type'].get(), description=fields['description'].get(), updated_by=None)
            else:
                upload_document(pid, title, document_type=fields['document_type'].get(), file_path=None, uploaded_by=None, description=fields['description'].get())
            top.destroy(); refresh()

        tk.Button(top, text='Save', command=_save, bg="#0EA5E9", fg='white', font=FONTS['body_bold']).pack(pady=12)

    def on_create():
        _open_form(None)

    def on_edit():
        sel = tree.selection()
        if not sel:
            messagebox.showinfo('Select', 'Select a document to edit')
            return
        values = tree.item(sel[0], 'values')
        doc = get_document(int(values[0]))
        if doc:
            _open_form(doc)

    def on_delete():
        sel = tree.selection()
        if not sel:
            messagebox.showinfo('Select', 'Select a document to delete')
            return
        values = tree.item(sel[0], 'values')
        did = int(values[0])
        if messagebox.askyesno('Confirm', 'Delete selected document?'):
            delete_document(did, deleted_by=None)
            refresh()

    tk.Button(btn_frame, text='New Document', command=on_create, bg="#06B6D4", fg='white', font=FONTS['body']).pack(fill='x', pady=4)
    tk.Button(btn_frame, text='Edit Document', command=on_edit, bg="#0EA5E9", fg='white', font=FONTS['body']).pack(fill='x', pady=4)
    tk.Button(btn_frame, text='Delete Document', command=on_delete, bg="#F43F5E", fg='white', font=FONTS['body']).pack(fill='x', pady=4)

    refresh()
