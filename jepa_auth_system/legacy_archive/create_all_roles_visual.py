#!/usr/bin/env python3
"""
Create visual evidence of all 9 roles with their module access.
"""
import sys
import tkinter as tk
from PIL import ImageGrab
import time

sys.path.insert(0, '.')

from jepa_site_manager.auth.roles import ROLE_LABELS, get_accessible_modules, get_role_label
from jepa_site_manager.auth.permissions import get_accessible_site_manager_actions

def create_roles_access_summary():
    """Create visual showing all 9 roles and their accessible modules."""
    root = tk.Tk()
    root.title("All 9 Roles - Module Access Summary")
    root.geometry("1000x600")
    root.configure(bg="#10263C")
    
    # Title
    title = tk.Label(root, text="REGISTRATION ROLE FIX - ALL 9 ROLES WITH PERMISSIONS", 
                     fg="#F0A500", bg="#10263C", font=("Segoe UI", 14, "bold"))
    title.pack(pady=15)
    
    # Create scrollable frame
    canvas = tk.Canvas(root, bg="#10263C", highlightthickness=0)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#10263C")
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Add role entries
    for role_key in sorted(ROLE_LABELS.keys()):
        role_label = get_role_label(role_key)
        accessible = sorted(get_accessible_modules(role_key))
        
        # Role frame
        role_frame = tk.Frame(scrollable_frame, bg="#17314A", highlightthickness=1, highlightbackground="#2A5A8C")
        role_frame.pack(fill="x", padx=12, pady=6)
        
        # Role header
        header = tk.Frame(role_frame, bg="#1F3A58")
        header.pack(fill="x")
        
        tk.Label(header, text=role_label, fg="#F0A500", bg="#1F3A58", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=12, pady=(6, 2))
        tk.Label(header, text=f"Accessible Modules: {len(accessible)}", fg="#A9C7E2", bg="#1F3A58", font=("Segoe UI", 8)).pack(anchor="w", padx=12, pady=(0, 6))
        
        # Modules list
        modules_text = ", ".join(accessible)
        modules_label = tk.Label(role_frame, text=modules_text, fg="#EAF4FF", bg="#17314A", justify="left", wraplength=900, font=("Courier", 8))
        modules_label.pack(anchor="w", padx=12, pady=(0, 8))
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    root.update()
    
    # Take screenshot
    time.sleep(0.5)
    try:
        x = root.winfo_rootx()
        y = root.winfo_rooty()
        w = root.winfo_width()
        h = root.winfo_height()
        
        screenshot = ImageGrab.grab(bbox=(x, y, x+w, y+h))
        screenshot.save("all_roles_permissions_summary.png")
        print("✓ Screenshot saved: all_roles_permissions_summary.png")
    except Exception as e:
        print(f"✗ Screenshot failed: {e}")
    
    root.after(2000, root.destroy)
    root.mainloop()

if __name__ == "__main__":
    print("Creating all roles permissions summary screenshot...")
    create_roles_access_summary()
