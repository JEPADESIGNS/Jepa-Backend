#!/usr/bin/env python3
"""Direct registration window for screenshot."""
import tkinter as tk
import sys

sys.path.insert(0, '.')

from auth.register import open_register_window

root = tk.Tk()
root.withdraw()

def callback():
    root.quit()

open_register_window(root, callback)
root.mainloop()
