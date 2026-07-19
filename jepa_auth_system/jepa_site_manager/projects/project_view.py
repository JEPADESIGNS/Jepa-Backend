"""Project Management view for JEPA Site Manager.

Full-featured project CRUD with project detail dashboard, statistics, and linked module access.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

from ui.themes import FONTS
from jepa_site_manager.projects.project_service import (
    create_project, get_project, list_projects, update_project, delete_project, get_project_stats
)
from jepa_site_manager.projects.models import ProjectRecord


def open_project_view(parent: tk.Misc, user_id: int | None = None) -> None:
    """Open the main project management view with CRUD and dashboard."""
    win = tk.Toplevel(parent)
    win.title("JEPA Site Manager — Projects")
    win.geometry("1100x700")
    win.configure(bg="#0F172A")
    
    # ============ HEADER ============
    header_frame = tk.Frame(win, bg="#0F172A")
    header_frame.pack(fill="x", padx=20, pady=(20, 10))
    
    tk.Label(
        header_frame, 
        text="PROJECT MANAGEMENT", 
        fg="#0EA5E9", 
        bg="#0F172A", 
        font=FONTS["h2"]
    ).pack(side="left")
    
    tk.Label(
        header_frame,
        text="[View: List | Create]",
        fg="#64748B",
        bg="#0F172A",
        font=FONTS["small"]
    ).pack(side="right")
    
    # ============ MAIN CONTAINER (List + Create panes) ============
    main_frame = tk.Frame(win, bg="#0F172A")
    main_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    # ---- LEFT: Project List ----
    left_pane = tk.Frame(main_frame, bg="#0F172A")
    left_pane.pack(side="left", fill="both", expand=True, padx=(0, 10))
    
    tk.Label(
        left_pane,
        text="ACTIVE PROJECTS",
        fg="#94A3B8",
        bg="#0F172A",
        font=("Arial", 11, "bold")
    ).pack(anchor="w", pady=(0, 8))
    
    # Filter controls
    filter_frame = tk.Frame(left_pane, bg="#1E293B", highlightthickness=1, highlightbackground="#334155")
    filter_frame.pack(fill="x", pady=(0, 10))
    
    tk.Label(filter_frame, text="Filter by status:", fg="#CBD5E1", bg="#1E293B", font=FONTS["small"]).pack(side="left", padx=8, pady=6)
    
    status_filter = tk.StringVar(value="All")
    for status in ["All", "Planning", "Active", "Completed", "On Hold", "Archived"]:
        tk.Radiobutton(
            filter_frame,
            text=status,
            variable=status_filter,
            value=status,
            bg="#1E293B",
            fg="#CBD5E1",
            selectcolor="#0EA5E9",
            font=FONTS["small"]
        ).pack(side="left", padx=2)
    
    # Project list treeview
    tree_frame = tk.Frame(left_pane, bg="#111827", highlightthickness=1, highlightbackground="#1F2937")
    tree_frame.pack(fill="both", expand=True)
    
    tree = ttk.Treeview(
        tree_frame,
        columns=("id", "name", "client", "status", "budget"),
        show="headings",
        height=20
    )
    tree.heading("id", text="ID")
    tree.heading("name", text="Project Name")
    tree.heading("client", text="Client")
    tree.heading("status", text="Status")
    tree.heading("budget", text="Budget ($)")
    
    tree.column("id", width=40)
    tree.column("name", width=280)
    tree.column("client", width=150)
    tree.column("status", width=100)
    tree.column("budget", width=100)
    
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(fill="both", expand=True)
    
    # ---- RIGHT: Project Details/Create Pane ----
    right_pane = tk.Frame(main_frame, bg="#1E293B", highlightthickness=1, highlightbackground="#334155", width=320)
    right_pane.pack(side="right", fill="both", padx=(10, 0))
    right_pane.pack_propagate(False)
    
    detail_frame = tk.Frame(right_pane, bg="#1E293B")
    detail_frame.pack(fill="both", expand=True, padx=12, pady=12)
    
    selected_project = {"id": None, "data": {}}
    
    # Detail view container
    detail_container = tk.Frame(detail_frame, bg="#1E293B")
    detail_container.pack(fill="both", expand=True)
    
    def clear_detail_frame():
        for widget in detail_container.winfo_children():
            widget.destroy()
    
    def show_project_detail(project_id: int):
        """Display detailed view of selected project."""
        clear_detail_frame()
        project = get_project(project_id)
        if not project:
            return
        
        selected_project["id"] = project_id
        selected_project["data"] = project
        
        # Title
        tk.Label(
            detail_container,
            text=project["project_name"][:25],
            fg="#F8FAFC",
            bg="#1E293B",
            font=("Arial", 12, "bold"),
            wraplength=280
        ).pack(anchor="w", pady=(0, 6))
        
        # Status badge
        status_color = {"Planning": "#94A3B8", "Active": "#10B981", "Completed": "#6366F1", "On Hold": "#F59E0B", "Archived": "#6B7280"}.get(project["status"], "#94A3B8")
        tk.Label(
            detail_container,
            text=f"Status: {project['status']}",
            fg=status_color,
            bg="#1E293B",
            font=FONTS["small"]
        ).pack(anchor="w", pady=2)
        
        # Details grid
        details = [
            ("Client", project.get("client") or "—"),
            ("Location", project.get("location") or "—"),
            ("Budget", f"${project.get('budget', 0):,.2f}"),
            ("Start", project.get("start_date") or "—"),
            ("End", project.get("end_date") or "—"),
        ]
        
        for label, value in details:
            tk.Label(detail_container, text=f"{label}:", fg="#94A3B8", bg="#1E293B", font=FONTS["small"]).pack(anchor="w", pady=(4, 0))
            tk.Label(detail_container, text=value, fg="#CBD5E1", bg="#1E293B", font=FONTS["small"], wraplength=280).pack(anchor="w")
        
        # Stats section
        try:
            stats = get_project_stats(project_id)
            if stats.get("project"):
                tk.Label(detail_container, text="", bg="#1E293B").pack()
                tk.Label(detail_container, text="STATS", fg="#94A3B8", bg="#1E293B", font=("Arial", 9, "bold")).pack(anchor="w", pady=(4, 2))
                
                stats_info = [
                    (f"Tasks", f"{stats['tasks']['completed']}/{stats['tasks']['total']} done"),
                    (f"Sites", str(stats['sites'])),
                    (f"Materials", f"{stats['materials']['total']} ({stats['materials']['low_stock']} low)"),
                    (f"Issues", str(stats['open_issues']) + " open"),
                ]
                
                for label, value in stats_info:
                    tk.Label(detail_container, text=f"{label}: {value}", fg="#CBD5E1", bg="#1E293B", font=FONTS["small"]).pack(anchor="w", pady=1)
        except:
            pass
        
        # Action buttons
        tk.Label(detail_container, text="", bg="#1E293B").pack(pady=6)
        
        def edit_project():
            show_edit_form(project_id)
        
        def delete_proj():
            if messagebox.askyesno("Confirm", f"Delete '{project['project_name']}'?\nLinked records will cause archival instead."):
                delete_project(project_id, user_id)
                refresh_list()
                clear_detail_frame()
        
        tk.Button(
            detail_container,
            text="Edit Project",
            command=edit_project,
            bg="#0EA5E9",
            fg="white",
            font=FONTS["small"],
            bd=0,
            cursor="hand2"
        ).pack(fill="x", pady=2)
        
        tk.Button(
            detail_container,
            text="Delete Project",
            command=delete_proj,
            bg="#EF4444",
            fg="white",
            font=FONTS["small"],
            bd=0,
            cursor="hand2"
        ).pack(fill="x", pady=2)
    
    def show_edit_form(project_id: int | None = None):
        """Show form to edit or create project."""
        clear_detail_frame()
        
        if project_id:
            project = get_project(project_id)
            title_text = "EDIT PROJECT"
            form_data = {
                "project_name": project.get("project_name", ""),
                "client": project.get("client", ""),
                "location": project.get("location", ""),
                "budget": str(project.get("budget", "")),
                "start_date": project.get("start_date", ""),
                "end_date": project.get("end_date", ""),
                "status": project.get("status", "Planning"),
            }
        else:
            title_text = "NEW PROJECT"
            form_data = {
                "project_name": "",
                "client": "",
                "location": "",
                "budget": "",
                "start_date": "",
                "end_date": "",
                "status": "Planning",
            }
        
        tk.Label(
            detail_container,
            text=title_text,
            fg="#0EA5E9",
            bg="#1E293B",
            font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(0, 8))
        
        fields = {}
        for label, field_name in [
            ("Project Name *", "project_name"),
            ("Client", "client"),
            ("Location", "location"),
            ("Budget ($)", "budget"),
            ("Start Date", "start_date"),
            ("End Date", "end_date"),
        ]:
            tk.Label(detail_container, text=label, fg="#94A3B8", bg="#1E293B", font=FONTS["small"]).pack(anchor="w", pady=(6, 2))
            var = tk.StringVar(value=form_data[field_name])
            entry = tk.Entry(
                detail_container,
                textvariable=var,
                bg="#0F172A",
                fg="#F8FAFC",
                bd=1,
                insertbackground="#F8FAFC",
                font=FONTS["small"]
            )
            entry.pack(fill="x")
            fields[field_name] = var
        
        tk.Label(detail_container, text="Status", fg="#94A3B8", bg="#1E293B", font=FONTS["small"]).pack(anchor="w", pady=(6, 2))
        status_var = tk.StringVar(value=form_data["status"])
        ttk.Combobox(
            detail_container,
            textvariable=status_var,
            values=["Planning", "Active", "Completed", "On Hold", "Archived"],
            state="readonly",
            font=FONTS["small"]
        ).pack(fill="x")
        fields["status"] = status_var
        
        def save_project():
            name = fields["project_name"].get().strip()
            if not name:
                messagebox.showerror("Error", "Project Name is required.")
                return
            
            try:
                budget = float(fields["budget"].get() or 0)
            except:
                messagebox.showerror("Error", "Budget must be a number.")
                return
            
            data = {
                "project_name": name,
                "client": fields["client"].get().strip() or None,
                "location": fields["location"].get().strip() or None,
                "budget": budget,
                "start_date": fields["start_date"].get().strip() or None,
                "end_date": fields["end_date"].get().strip() or None,
                "status": fields["status"].get(),
            }
            
            if project_id:
                update_project(project_id, data, user_id)
                messagebox.showinfo("Success", "Project updated.")
            else:
                create_project(
                    ProjectRecord(**data, created_by=user_id),
                    user_id
                )
                messagebox.showinfo("Success", "Project created.")
            
            refresh_list()
            clear_detail_frame()
        
        tk.Button(
            detail_container,
            text="Save",
            command=save_project,
            bg="#10B981",
            fg="white",
            font=FONTS["small"],
            bd=0,
            cursor="hand2"
        ).pack(fill="x", pady=(12, 2))
        
        tk.Button(
            detail_container,
            text="Cancel",
            command=lambda: clear_detail_frame(),
            bg="#475569",
            fg="white",
            font=FONTS["small"],
            bd=0,
            cursor="hand2"
        ).pack(fill="x")
    
    def refresh_list():
        """Refresh project list based on filter."""
        for item in tree.get_children():
            tree.delete(item)
        
        filter_val = status_filter.get()
        projects = list_projects(filter_val if filter_val != "All" else None)
        
        for proj in projects:
            tree.insert("", "end", values=(
                proj["id"],
                proj["project_name"],
                proj["client"] or "—",
                proj["status"],
                f"${proj['budget']:,.0f}" if proj['budget'] else "—"
            ))
    
    def on_tree_select(_event):
        """Handle project selection."""
        selection = tree.selection()
        if selection:
            item = selection[0]
            values = tree.item(item, "values")
            project_id = int(values[0])
            show_project_detail(project_id)
    
    def on_filter_change(*_args):
        """Handle status filter change."""
        refresh_list()
    
    tree.bind("<<TreeviewSelect>>", on_tree_select)
    status_filter.trace("w", on_filter_change)
    
    # ============ FOOTER: Action Buttons ============
    footer_frame = tk.Frame(win, bg="#0F172A")
    footer_frame.pack(fill="x", padx=20, pady=(10, 20))
    
    tk.Button(
        footer_frame,
        text="+ NEW PROJECT",
        command=lambda: show_edit_form(),
        bg="#0EA5E9",
        fg="white",
        font=FONTS["body_bold"],
        bd=0,
        cursor="hand2",
        padx=16,
        pady=6
    ).pack(side="left")
    
    tk.Button(
        footer_frame,
        text="REFRESH",
        command=refresh_list,
        bg="#475569",
        fg="white",
        font=FONTS["body"],
        bd=0,
        cursor="hand2",
        padx=12,
        pady=6
    ).pack(side="left", padx=6)
    
    # Initial load
    refresh_list()


# Backward compatibility
open_project_manager = open_project_view
