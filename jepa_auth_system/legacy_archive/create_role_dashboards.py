#!/usr/bin/env python3
"""Create dashboard screenshots for each role."""
import sys
import tkinter as tk
from PIL import ImageGrab
import time

sys.path.insert(0, '.')

from database.db import get_connection
from auth.security import verify_password
from jepa_site_manager.auth.roles import get_role_label, get_accessible_modules
from jepa_site_manager.auth.permissions import get_accessible_site_manager_actions

TEST_ACCOUNTS = [
    ("test_superadmin", "TestPass123!@#", "super_admin"),
    ("test_admin", "TestPass123!@#", "admin"),
    ("test_contractor", "TestPass123!@#", "contractor"),
    ("test_projmgr", "TestPass123!@#", "project_manager"),
    ("test_siteengineer", "TestPass123!@#", "site_engineer"),
    ("test_storekeeper", "TestPass123!@#", "store_keeper"),
    ("test_equipofficer", "TestPass123!@#", "equipment_officer"),
    ("test_client", "TestPass123!@#", "client"),
    ("test_consultant", "TestPass123!@#", "consultant"),
]

def create_dashboard_screenshot(username, authenticated_role, role_label, user_id, email):
    """Create a simulated dashboard screenshot."""
    root = tk.Tk()
    root.title(f"Dashboard - {role_label}")
    root.geometry("900x500")
    root.configure(bg="#0F172A")
    
    # Header
    header_frame = tk.Frame(root, bg="#1E293B")
    header_frame.pack(fill="x")
    
    tk.Label(header_frame, text="JEPA SITE MANAGER — DASHBOARD", fg="#F59E0B", bg="#1E293B", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=20, pady=(12, 4))
    
    user_info = tk.Frame(header_frame, bg="#1E293B")
    user_info.pack(anchor="w", padx=20, pady=(0, 12), fill="x")
    
    tk.Label(user_info, text=f"Logged in as: {username} (ID: {user_id}) | Role: {role_label} | Email: {email}", fg="#CBD5E1", bg="#1E293B", font=("Courier", 9)).pack(anchor="w")
    
    # Content
    content_frame = tk.Frame(root, bg="#0F172A")
    content_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    tk.Label(content_frame, text="Dashboard Access", fg="#F59E0B", bg="#0F172A", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 10))
    
    # Modules panel
    modules_frame = tk.Frame(content_frame, bg="#1E293B", highlightthickness=1, highlightbackground="#475569")
    modules_frame.pack(fill="both", expand=True)
    
    accessible = sorted(get_accessible_modules(authenticated_role))
    
    tk.Label(modules_frame, text=f"Accessible Modules ({len(accessible)})", fg="#F59E0B", bg="#1E293B", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=12, pady=(8, 4))
    
    modules_text = ", ".join(accessible)
    tk.Label(modules_frame, text=modules_text, fg="#E2E8F0", bg="#1E293B", justify="left", wraplength=800, font=("Courier", 9)).pack(anchor="w", padx=12, pady=(0, 12))
    
    root.update()
    
    # Screenshot
    time.sleep(0.3)
    try:
        x = root.winfo_rootx()
        y = root.winfo_rooty()
        w = root.winfo_width()
        h = root.winfo_height()
        
        screenshot = ImageGrab.grab(bbox=(x, y, x+w, y+h))
        safe_role = authenticated_role.replace("_", "")
        filename = f"dashboard_{safe_role}.png"
        screenshot.save(filename)
        print(f"✓ {role_label:20s} - Screenshot: {filename}")
    except Exception as e:
        print(f"✗ {role_label:20s} - Screenshot failed: {e}")
    
    root.after(500, root.destroy)
    root.mainloop()

print("Creating dashboard screenshots for all 9 roles...\n")

with get_connection() as conn:
    import sqlite3
    conn.row_factory = sqlite3.Row
    
    for username, password, expected_role in TEST_ACCOUNTS:
        # Get user
        user = conn.execute(
            "SELECT id, username, email, role, password_hash, full_name FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        
        if not user:
            print(f"✗ {expected_role:20s} - User not found")
            continue
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            print(f"✗ {expected_role:20s} - Password verification failed")
            continue
        
        authenticated_role = user['role']
        role_label = get_role_label(authenticated_role)
        
        # Create screenshot
        create_dashboard_screenshot(
            username,
            authenticated_role,
            role_label,
            user['id'],
            user['email']
        )

print("\nAll screenshots completed.")
