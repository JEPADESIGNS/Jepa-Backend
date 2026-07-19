"""Basic site management view for JEPA Site Manager."""

import tkinter as tk
from tkinter import ttk

from ui.themes import FONTS
from jepa_site_manager.sites.site_service import create_site, list_sites


def open_site_view(parent: tk.Misc, user_id: int | None = None, default_project_id: int | None = None) -> None:
    """Open a simple site management window."""
    win = tk.Toplevel(parent)
    win.title("JEPA Site Manager — Sites")
    win.geometry("900x520")
    win.configure(bg="#0F172A")

    tk.Label(win, text="SITE MANAGEMENT", fg="#0EA5E9", bg="#0F172A", font=FONTS["h2"]).pack(pady=(18, 6))
    tk.Label(win, text="Create and review operational sites for each project.", fg="#94A3B8", bg="#0F172A", font=FONTS["small"]).pack()

    form = tk.Frame(win, bg="#0F172A")
    form.pack(fill="x", padx=18, pady=10)

    filter_label = tk.Label(win, text="Showing all sites" if default_project_id is None else f"Showing sites for project {default_project_id}", fg="#E2E8F0", bg="#0F172A", font=FONTS["small"])
    filter_label.pack(anchor="w", padx=18)

    fields = {
        "project_id": tk.StringVar(value=str(default_project_id) if default_project_id is not None else ""),
        "site_name": tk.StringVar(),
        "location": tk.StringVar(),
        "site_type": tk.StringVar(value="Main Site"),
        "status": tk.StringVar(value="Active"),
    }

    for label, var in [
        ("Project ID", fields["project_id"]),
        ("Site Name", fields["site_name"]),
        ("Location", fields["location"]),
        ("Site Type", fields["site_type"]),
        ("Status", fields["status"]),
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

        site_id = create_site(
            project_id=project_id,
            site_name=fields["site_name"].get().strip(),
            location=fields["location"].get().strip(),
            site_type=fields["site_type"].get().strip() or "Main Site",
            status=fields["status"].get().strip() or "Active",
            responsible_user_id=user_id,
        )
        tk.messagebox.showinfo("Saved", f"Site created with id {site_id}.")
        _refresh()

    tk.Button(form, text="Save Site", command=_save, bg="#0EA5E9", fg="white", font=FONTS["body_bold"], bd=0, cursor="hand2").pack(pady=(10, 0), ipady=4)

    tree = ttk.Treeview(win, columns=("id", "project_id", "name", "location", "type", "status"), show="headings")
    tree.heading("id", text="ID")
    tree.heading("project_id", text="Project ID")
    tree.heading("name", text="Site Name")
    tree.heading("location", text="Location")
    tree.heading("type", text="Type")
    tree.heading("status", text="Status")
    tree.pack(fill="both", expand=True, padx=18, pady=(10, 18))

    def _refresh() -> None:
        for item in tree.get_children():
            tree.delete(item)
        rows = list_sites(default_project_id) if default_project_id is not None else list_sites()
        for row in rows:
            tree.insert("", "end", values=(row["id"], row["project_id"], row["site_name"], row["location"] or "", row["site_type"], row["status"]))

    _refresh()
