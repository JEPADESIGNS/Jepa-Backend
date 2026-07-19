"""Material Management view for JEPA Site Manager."""

import tkinter as tk
from tkinter import ttk

from ui.themes import FONTS
from jepa_site_manager.materials.material_service import create_material, list_materials


def open_material_view(parent: tk.Misc, user_id: int | None = None, default_project_id: int | None = None) -> None:
    """Open a basic material management window."""
    win = tk.Toplevel(parent)
    win.title("JEPA Site Manager — Materials")
    win.geometry("980x520")
    win.configure(bg="#0F172A")

    tk.Label(win, text="MATERIAL MANAGEMENT", fg="#0EA5E9", bg="#0F172A", font=FONTS["h2"]).pack(pady=(18, 6))
    tk.Label(win, text="Track material receipts, issues, and balances by project.", fg="#94A3B8", bg="#0F172A", font=FONTS["small"]).pack()

    form = tk.Frame(win, bg="#0F172A")
    form.pack(fill="x", padx=18, pady=10)

    fields = {
        "project_id": tk.StringVar(value=str(default_project_id) if default_project_id is not None else ""),
        "material_name": tk.StringVar(),
        "quantity": tk.StringVar(),
        "supplier": tk.StringVar(),
        "date_received": tk.StringVar(),
        "date_issued": tk.StringVar(),
        "balance": tk.StringVar(),
    }

    for label, var in [
        ("Project ID", fields["project_id"]),
        ("Material Name", fields["material_name"]),
        ("Quantity", fields["quantity"]),
        ("Supplier", fields["supplier"]),
        ("Date Received", fields["date_received"]),
        ("Date Issued", fields["date_issued"]),
        ("Balance", fields["balance"]),
    ]:
        row = tk.Frame(form, bg="#0F172A")
        row.pack(fill="x", pady=3)
        tk.Label(row, text=label, fg="#94A3B8", bg="#0F172A", font=FONTS["label"]).pack(side="left", anchor="w")
        tk.Entry(row, textvariable=var, bg="#334155", fg="#F8FAFC", bd=0, insertbackground="#F8FAFC", font=FONTS["body"]).pack(side="left", fill="x", expand=True)

    def _save() -> None:
        try:
            project_id = int(fields["project_id"].get().strip())
            quantity = float(fields["quantity"].get().strip() or 0)
            balance = float(fields["balance"].get().strip() or quantity)
        except ValueError:
            tk.messagebox.showwarning("Required", "Project ID, Quantity, and Balance must be numeric.")
            return

        material_id = create_material(
            project_id=project_id,
            material_name=fields["material_name"].get().strip(),
            quantity=quantity,
            supplier=fields["supplier"].get().strip(),
            date_received=fields["date_received"].get().strip() or None,
            date_issued=fields["date_issued"].get().strip() or None,
            balance=balance,
            created_by=user_id,
        )
        tk.messagebox.showinfo("Saved", f"Material record created with id {material_id}.")
        _refresh()

    tk.Button(form, text="Save Material Record", command=_save, bg="#0EA5E9", fg="white", font=FONTS["body_bold"], bd=0, cursor="hand2").pack(pady=(10, 0), ipady=4)

    tree = ttk.Treeview(win, columns=("id", "project_id", "name", "quantity", "supplier", "balance"), show="headings")
    tree.heading("id", text="ID")
    tree.heading("project_id", text="Project ID")
    tree.heading("name", text="Material")
    tree.heading("quantity", text="Quantity")
    tree.heading("supplier", text="Supplier")
    tree.heading("balance", text="Balance")
    tree.pack(fill="both", expand=True, padx=18, pady=(10, 18))

    def _refresh() -> None:
        for item in tree.get_children():
            tree.delete(item)
        for row in list_materials():
            tree.insert("", "end", values=(row["id"], row["project_id"], row["material_name"], row["quantity"], row["supplier"] or "", row["balance"]))

    _refresh()
