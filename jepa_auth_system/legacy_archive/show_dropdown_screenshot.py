#!/usr/bin/env python3
"""Display registration window and save screenshot of role dropdown."""
import sys
import tkinter as tk
from tkinter import ttk
from PIL import ImageGrab, Image
import time

sys.path.insert(0, '.')

from auth.register import ROLE_CHOICES
from jepa_site_manager.auth.roles import ROLE_LABELS, USER_ROLES

# Create a simple window showing the role dropdown
root = tk.Tk()
root.title("Registration - Role Dropdown (9 roles)")
root.geometry("500x300")
root.configure(bg="#10263C")

# Add title
title = tk.Label(root, text="REGISTRATION ROLE DROPDOWN", fg="#EAF4FF", bg="#10263C", font=("Segoe UI", 14, "bold"))
title.pack(pady=20)

# Add subtitle showing centralized source
subtitle = tk.Label(root, text="Roles loaded from: jepa_site_manager/auth/roles.py (USER_ROLES)", fg="#A9C7E2", bg="#10263C", font=("Segoe UI", 10))
subtitle.pack(pady=(0, 20))

# Extract role labels for dropdown
role_labels = [label for label, _ in ROLE_CHOICES]

# Create frame for dropdown
frame = tk.Frame(root, bg="#17314A", highlightthickness=1, highlightbackground="#2A5A8C")
frame.pack(padx=20, pady=10, fill="x")

label = tk.Label(frame, text="Select Your Role:", fg="#F0A500", bg="#17314A", font=("Segoe UI", 10, "bold"))
label.pack(anchor="w", padx=12, pady=(8, 4))

role_var = tk.StringVar(value=role_labels[0] if role_labels else "Client")
combo = ttk.Combobox(frame, textvariable=role_var, values=role_labels, state="readonly", width=40)
combo.pack(fill="x", padx=12, pady=(0, 12))

# Show all roles in a list
info_frame = tk.Frame(root, bg="#10263C")
info_frame.pack(padx=20, pady=10, fill="both", expand=True)

info_label = tk.Label(info_frame, text="All 9 Available Roles:", fg="#EAF4FF", bg="#10263C", font=("Segoe UI", 10, "bold"))
info_label.pack(anchor="w")

roles_text = "\n".join([f"{i}. {label}" for i, (label, _) in enumerate(sorted(ROLE_CHOICES), 1)])
roles_display = tk.Label(info_frame, text=roles_text, fg="#EAF4FF", bg="#10263C", justify="left", font=("Courier", 9))
roles_display.pack(anchor="w", pady=5)

# Update the window
root.update()

# Take a screenshot
time.sleep(0.5)
try:
    # Get window position and size
    x = root.winfo_rootx()
    y = root.winfo_rooty()
    w = root.winfo_width()
    h = root.winfo_height()
    
    # Capture screenshot
    screenshot = ImageGrab.grab(bbox=(x, y, x+w, y+h))
    screenshot.save("registration_dropdown_screenshot.png")
    print("Screenshot saved: registration_dropdown_screenshot.png")
    print(f"Window dimensions: {w}x{h}")
except Exception as e:
    print(f"Could not save screenshot: {e}")

# Keep window visible briefly
root.after(500, root.destroy)
root.mainloop()

print("\nRegistration dropdown now displays all 9 roles:")
for i, (label, key) in enumerate(sorted(ROLE_CHOICES), 1):
    print(f"  {i}. {label:25s} (backend value: {key})")
