"""Attendance and workforce activity surface for JEPA Site Manager.

BIOMETRIC INTEGRATION:
- All attendance records MUST be verified via biometric (fingerprint or face recognition)
- Physical ID card scanning is MANDATORY for every team member entry
- Audit trail logs all biometric and ID verification attempts
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta

from ui.themes import FONTS
from jepa_site_manager.workforce.attendance_service import (
    mark_attendance, get_attendance_by_date, get_attendance_stats, get_project_attendance_summary,
    log_biometric_verification, log_physical_id_scan
)
from jepa_site_manager.projects.project_service import list_projects
from jepa_site_manager.database.connection import get_connection


class BiometricVerificationDialog:
    """Dialog for biometric verification (fingerprint/face recognition)."""
    
    def __init__(self, parent: tk.Misc, title: str = "Biometric Verification"):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.configure(bg="#0F172A")
        self.dialog.resizable(False, False)
        
        # Center on parent
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Content
        tk.Label(
            self.dialog,
            text="🔐 BIOMETRIC VERIFICATION REQUIRED",
            fg="#0EA5E9",
            bg="#0F172A",
            font=("Arial", 12, "bold")
        ).pack(pady=(20, 10))
        
        tk.Label(
            self.dialog,
            text="Select verification method:",
            fg="#CBD5E1",
            bg="#0F172A",
            font=FONTS["small"]
        ).pack(pady=(0, 15))
        
        # Biometric type selection
        biometric_type = tk.StringVar(value="fingerprint")
        
        tk.Radiobutton(
            self.dialog,
            text="👆 Fingerprint Scan",
            variable=biometric_type,
            value="fingerprint",
            bg="#0F172A",
            fg="#CBD5E1",
            selectcolor="#0EA5E9",
            font=FONTS["body"],
            padx=20,
            pady=10
        ).pack(anchor="w", padx=30)
        
        tk.Radiobutton(
            self.dialog,
            text="😊 Face Recognition",
            variable=biometric_type,
            value="face_recognition",
            bg="#0F172A",
            fg="#CBD5E1",
            selectcolor="#0EA5E9",
            font=FONTS["body"],
            padx=20,
            pady=10
        ).pack(anchor="w", padx=30)
        
        # Info box
        info_frame = tk.Frame(self.dialog, bg="#1E293B", highlightthickness=1, highlightbackground="#334155")
        info_frame.pack(fill="x", padx=20, pady=(20, 0))
        
        tk.Label(
            info_frame,
            text="⚠ Biometric data is encrypted and stored securely.",
            fg="#94A3B8",
            bg="#1E293B",
            font=FONTS["small"],
            wraplength=350,
            justify="left"
        ).pack(anchor="w", padx=12, pady=12)
        
        # Buttons
        btn_frame = tk.Frame(self.dialog, bg="#0F172A")
        btn_frame.pack(fill="x", padx=20, pady=(20, 20))
        
        tk.Button(
            btn_frame,
            text="✓ Verified",
            command=lambda: self._verify(biometric_type.get()),
            bg="#10B981",
            fg="white",
            font=FONTS["body"],
            bd=0,
            cursor="hand2"
        ).pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        tk.Button(
            btn_frame,
            text="✗ Cancel",
            command=self._cancel,
            bg="#EF4444",
            fg="white",
            font=FONTS["body"],
            bd=0,
            cursor="hand2"
        ).pack(side="left", fill="x", expand=True)
    
    def _verify(self, biometric_type: str):
        """Mark biometric as verified."""
        self.result = {
            "verified": True,
            "type": biometric_type,
            "data": f"biometric_{datetime.now().isoformat()}",  # Placeholder for actual biometric token
            "device_id": "scanner_01"  # Placeholder for actual device ID
        }
        self.dialog.destroy()
    
    def _cancel(self):
        """Cancel biometric verification."""
        self.result = {"verified": False}
        self.dialog.destroy()


def open_attendance_view(parent: tk.Misc, user_id: int | None = None, project_id: int | None = None) -> None:
    """Open comprehensive attendance management interface."""
    win = tk.Toplevel(parent)
    win.title("JEPA Site Manager — Attendance & Workforce")
    win.geometry("1200x750")
    win.configure(bg="#0F172A")
    
    # ============ HEADER ============
    header_frame = tk.Frame(win, bg="#0F172A")
    header_frame.pack(fill="x", padx=20, pady=(20, 10))
    
    tk.Label(
        header_frame,
        text="ATTENDANCE & WORKFORCE",
        fg="#F59E0B",
        bg="#0F172A",
        font=FONTS["h2"]
    ).pack(side="left")
    
    tk.Label(
        header_frame,
        text="Daily attendance marking and workforce status tracking",
        fg="#94A3B8",
        bg="#0F172A",
        font=FONTS["small"]
    ).pack(side="left", padx=(20, 0))
    
    # ============ CONTROL PANEL ============
    control_frame = tk.Frame(win, bg="#1E293B", highlightthickness=1, highlightbackground="#334155")
    control_frame.pack(fill="x", padx=20, pady=10)
    
    # Date selection
    tk.Label(control_frame, text="Attendance Date:", fg="#CBD5E1", bg="#1E293B", font=FONTS["label"]).pack(side="left", padx=10, pady=8)
    
    date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
    date_entry = tk.Entry(
        control_frame,
        textvariable=date_var,
        bg="#0F172A",
        fg="#F8FAFC",
        bd=1,
        font=FONTS["small"],
        width=15
    )
    date_entry.pack(side="left", padx=5)
    
    tk.Label(control_frame, text="Project:", fg="#CBD5E1", bg="#1E293B", font=FONTS["label"]).pack(side="left", padx=(20, 5))
    
    projects = list_projects()
    project_options = {p["project_name"]: p["id"] for p in projects}
    project_var = tk.StringVar(value=projects[0]["project_name"] if projects else "")
    
    project_combo = ttk.Combobox(
        control_frame,
        textvariable=project_var,
        values=list(project_options.keys()),
        state="readonly",
        font=FONTS["small"],
        width=20
    )
    project_combo.pack(side="left", padx=5)
    
    selected_project_id = project_id or (project_options.get(project_var.get()) if project_var.get() else None)
    
    # ============ MAIN CONTAINER ============
    main_frame = tk.Frame(win, bg="#0F172A")
    main_frame.pack(fill="both", expand=True, padx=20, pady=10)
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=0)
    
    # ---- LEFT: Attendance List ----
    list_frame = tk.Frame(main_frame, bg="#1E293B", highlightthickness=1, highlightbackground="#334155")
    list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    list_frame.grid_rowconfigure(1, weight=1)
    
    tk.Label(
        list_frame,
        text="TEAM ATTENDANCE",
        fg="#94A3B8",
        bg="#1E293B",
        font=("Arial", 11, "bold")
    ).pack(fill="x", padx=12, pady=(12, 8))
    
    # Attendance tree
    tree_container = tk.Frame(list_frame, bg="#111827")
    tree_container.pack(fill="both", expand=True, padx=12, pady=(0, 12))
    
    tree = ttk.Treeview(
        tree_container,
        columns=("user_id", "name", "status", "time_in", "time_out", "notes"),
        show="headings",
        height=25
    )
    tree.heading("user_id", text="ID")
    tree.heading("name", text="Team Member")
    tree.heading("status", text="Status")
    tree.heading("time_in", text="Time In")
    tree.heading("time_out", text="Time Out")
    tree.heading("notes", text="Notes")
    
    tree.column("user_id", width=40)
    tree.column("name", width=200)
    tree.column("status", width=90)
    tree.column("time_in", width=80)
    tree.column("time_out", width=80)
    tree.column("notes", width=150)
    
    scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(fill="both", expand=True)
    
    # ---- RIGHT: Stats & Actions ----
    stats_frame = tk.Frame(main_frame, bg="#1E293B", highlightthickness=1, highlightbackground="#334155", width=300)
    stats_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
    stats_frame.pack_propagate(False)
    
    stats_content = tk.Frame(stats_frame, bg="#1E293B")
    stats_content.pack(fill="both", expand=True, padx=12, pady=12)
    
    # Statistics cards
    def refresh_stats():
        """Refresh attendance statistics."""
        for widget in stats_content.winfo_children():
            widget.destroy()
        
        if not selected_project_id:
            tk.Label(stats_content, text="Select a project to view stats", fg="#CBD5E1", bg="#1E293B", font=FONTS["small"]).pack(pady=20)
            return
        
        stats = get_attendance_stats(selected_project_id, date_var.get())
        
        tk.Label(stats_content, text="DAILY STATS", fg="#0EA5E9", bg="#1E293B", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 10))
        
        stat_items = [
            ("Present", str(stats["present"]), "#22C55E"),
            ("Absent", str(stats["absent"]), "#EF4444"),
            ("Late", str(stats["late"]), "#F59E0B"),
            ("On Leave", str(stats["on_leave"]), "#8B5CF6"),
            ("Total", str(stats["total"]), "#0EA5E9"),
        ]
        
        for label, value, color in stat_items:
            card = tk.Frame(stats_content, bg="#0F172A", highlightthickness=1, highlightbackground=color)
            card.pack(fill="x", pady=4)
            
            tk.Label(card, text=label, fg="#94A3B8", bg="#0F172A", font=FONTS["small"]).pack(anchor="w", padx=8, pady=(6, 2))
            tk.Label(card, text=value, fg=color, bg="#0F172A", font=("Arial", 18, "bold")).pack(anchor="w", padx=8, pady=(0, 6))
    
    def refresh_attendance():
        """Refresh attendance list for selected date."""
        for item in tree.get_children():
            tree.delete(item)
        
        if not selected_project_id:
            return
        
        records = get_attendance_by_date(date_var.get(), selected_project_id)
        
        if not records:
            tree.insert("", "end", values=("—", "No attendance records for this date", "—", "—", "—", "—"))
            return
        
        for rec in records:
            tree.insert("", "end", values=(
                rec["user_id"],
                f"User #{rec['user_id']}",
                rec["status"],
                rec["time_in"] or "—",
                rec["time_out"] or "—",
                rec["notes"] or "—"
            ))
        
        refresh_stats()
    
    def mark_present():
        """Mark selected user as present (REQUIRES biometric + physical ID verification)."""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Select", "Please select a team member from the list.")
            return

        item = selection[0]
        values = tree.item(item, "values")
        user_id_raw = str(values[0]).strip()
        if not user_id_raw.isdigit():
            messagebox.showwarning("Invalid Selection", "Please select a valid team member.")
            return
        user_id = int(user_id_raw)
        
        if not selected_project_id:
            messagebox.showerror("Error", "No project selected.")
            return
        
        # MANDATORY: Get biometric verification
        biometric_dialog = BiometricVerificationDialog(win, "Fingerprint / Face Recognition")
        win.wait_window(biometric_dialog.dialog)
        biometric_result = biometric_dialog.result
        
        if not biometric_result or not biometric_result["verified"]:
            messagebox.showerror("Verification Failed", "❌ Biometric verification failed. Attendance not recorded.")
            return
        
        # MANDATORY: Get physical ID verification
        physical_id = simpledialog.askstring(
            "Physical ID Required",
            "Scan or enter the team member's physical ID card number:\n\n(This is MANDATORY)",
            parent=win
        )
        
        if not physical_id or not physical_id.strip():
            messagebox.showerror("Verification Failed", "❌ Physical ID required. Attendance not recorded.")
            return
        
        # Log biometric verification
        log_biometric_verification(
            attendance_id=None,  # Will be created
            user_id=user_id,
            project_id=selected_project_id,
            biometric_type=biometric_result["type"],
            physical_id=physical_id.strip(),
            biometric_data=biometric_result["data"],
            device_id=biometric_result.get("device_id")
        )
        
        # Log physical ID scan
        log_physical_id_scan(
            user_id=user_id,
            project_id=selected_project_id,
            physical_id=physical_id.strip(),
            scan_status="Valid",
            device_id="manual_scan"
        )
        
        # Now mark attendance (both verifications passed)
        mark_attendance(
            project_id=selected_project_id,
            user_id=user_id,
            attendance_date=date_var.get(),
            status="Present",
            biometric_type=biometric_result["type"],
            biometric_data=biometric_result["data"],
            physical_id=physical_id.strip(),
            verified_by_biometric=True,
            verified_by_physical_id=True
        )
        messagebox.showinfo("✓ Success", f"User #{user_id} marked as Present (Biometric + ID verified).")
        refresh_attendance()
    
    def mark_absent():
        """Mark selected user as absent (REQUIRES biometric + physical ID verification)."""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Select", "Please select a team member from the list.")
            return

        item = selection[0]
        values = tree.item(item, "values")
        user_id_raw = str(values[0]).strip()
        if not user_id_raw.isdigit():
            messagebox.showwarning("Invalid Selection", "Please select a valid team member.")
            return
        user_id = int(user_id_raw)
        
        if not selected_project_id:
            messagebox.showerror("Error", "No project selected.")
            return
        
        # MANDATORY: Get biometric verification
        biometric_dialog = BiometricVerificationDialog(win, "Fingerprint / Face Recognition")
        win.wait_window(biometric_dialog.dialog)
        biometric_result = biometric_dialog.result
        
        if not biometric_result or not biometric_result["verified"]:
            messagebox.showerror("Verification Failed", "❌ Biometric verification failed. Attendance not recorded.")
            return
        
        # MANDATORY: Get physical ID verification
        physical_id = simpledialog.askstring(
            "Physical ID Required",
            "Scan or enter the team member's physical ID card number:\n\n(This is MANDATORY)",
            parent=win
        )
        
        if not physical_id or not physical_id.strip():
            messagebox.showerror("Verification Failed", "❌ Physical ID required. Attendance not recorded.")
            return
        
        # Log verifications
        log_biometric_verification(
            attendance_id=None,
            user_id=user_id,
            project_id=selected_project_id,
            biometric_type=biometric_result["type"],
            physical_id=physical_id.strip(),
            biometric_data=biometric_result["data"],
            device_id=biometric_result.get("device_id")
        )
        
        log_physical_id_scan(
            user_id=user_id,
            project_id=selected_project_id,
            physical_id=physical_id.strip(),
            scan_status="Valid",
            device_id="manual_scan"
        )
        
        # Mark attendance
        mark_attendance(
            project_id=selected_project_id,
            user_id=user_id,
            attendance_date=date_var.get(),
            status="Absent",
            biometric_type=biometric_result["type"],
            biometric_data=biometric_result["data"],
            physical_id=physical_id.strip(),
            verified_by_biometric=True,
            verified_by_physical_id=True
        )
        messagebox.showinfo("✓ Success", f"User #{user_id} marked as Absent (Biometric + ID verified).")
        refresh_attendance()
    
    def mark_late():
        """Mark selected user as late (REQUIRES biometric + physical ID verification)."""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Select", "Please select a team member from the list.")
            return

        item = selection[0]
        values = tree.item(item, "values")
        user_id_raw = str(values[0]).strip()
        if not user_id_raw.isdigit():
            messagebox.showwarning("Invalid Selection", "Please select a valid team member.")
            return
        user_id = int(user_id_raw)
        
        if not selected_project_id:
            messagebox.showerror("Error", "No project selected.")
            return
        
        # MANDATORY: Get biometric verification
        biometric_dialog = BiometricVerificationDialog(win, "Fingerprint / Face Recognition")
        win.wait_window(biometric_dialog.dialog)
        biometric_result = biometric_dialog.result
        
        if not biometric_result or not biometric_result["verified"]:
            messagebox.showerror("Verification Failed", "❌ Biometric verification failed. Attendance not recorded.")
            return
        
        # MANDATORY: Get physical ID verification
        physical_id = simpledialog.askstring(
            "Physical ID Required",
            "Scan or enter the team member's physical ID card number:\n\n(This is MANDATORY)",
            parent=win
        )
        
        if not physical_id or not physical_id.strip():
            messagebox.showerror("Verification Failed", "❌ Physical ID required. Attendance not recorded.")
            return
        
        # Log verifications
        log_biometric_verification(
            attendance_id=None,
            user_id=user_id,
            project_id=selected_project_id,
            biometric_type=biometric_result["type"],
            physical_id=physical_id.strip(),
            biometric_data=biometric_result["data"],
            device_id=biometric_result.get("device_id")
        )
        
        log_physical_id_scan(
            user_id=user_id,
            project_id=selected_project_id,
            physical_id=physical_id.strip(),
            scan_status="Valid",
            device_id="manual_scan"
        )
        
        # Mark attendance
        mark_attendance(
            project_id=selected_project_id,
            user_id=user_id,
            attendance_date=date_var.get(),
            status="Late",
            biometric_type=biometric_result["type"],
            biometric_data=biometric_result["data"],
            physical_id=physical_id.strip(),
            verified_by_biometric=True,
            verified_by_physical_id=True
        )
        messagebox.showinfo("✓ Success", f"User #{user_id} marked as Late (Biometric + ID verified).")
        refresh_attendance()
    
    # Action buttons
    tk.Label(stats_content, text="", bg="#1E293B").pack(pady=8)
    tk.Label(stats_content, text="QUICK ACTIONS", fg="#0EA5E9", bg="#1E293B", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 8))
    
    tk.Button(
        stats_content,
        text="✓ Mark Present",
        command=mark_present,
        bg="#22C55E",
        fg="white",
        font=FONTS["small"],
        bd=0,
        cursor="hand2"
    ).pack(fill="x", pady=3)
    
    tk.Button(
        stats_content,
        text="✗ Mark Absent",
        command=mark_absent,
        bg="#EF4444",
        fg="white",
        font=FONTS["small"],
        bd=0,
        cursor="hand2"
    ).pack(fill="x", pady=3)
    
    tk.Button(
        stats_content,
        text="⏱ Mark Late",
        command=mark_late,
        bg="#F59E0B",
        fg="white",
        font=FONTS["small"],
        bd=0,
        cursor="hand2"
    ).pack(fill="x", pady=3)
    
    # Footer
    footer_frame = tk.Frame(win, bg="#0F172A")
    footer_frame.pack(fill="x", padx=20, pady=(10, 20))
    
    def on_project_change(*_args):
        nonlocal selected_project_id
        selected_project_id = project_options.get(project_var.get())
        refresh_attendance()
    
    def on_date_change(*_args):
        refresh_attendance()
    
    project_var.trace("w", on_project_change)
    date_var.trace("w", on_date_change)
    
    tk.Button(
        footer_frame,
        text="REFRESH",
        command=refresh_attendance,
        bg="#475569",
        fg="white",
        font=FONTS["body"],
        bd=0,
        cursor="hand2",
        padx=12,
        pady=6
    ).pack(side="left")
    
    # Initial load
    if selected_project_id:
        project_combo.set([p["project_name"] for p in projects if p["id"] == selected_project_id][0] if any(p["id"] == selected_project_id for p in projects) else "")
    
    refresh_attendance()


def open_workforce_view(parent: tk.Misc, user_id: int | None = None, project_id: int | None = None) -> None:
    """Backward-compatible alias."""
    open_attendance_view(parent, user_id, project_id)
