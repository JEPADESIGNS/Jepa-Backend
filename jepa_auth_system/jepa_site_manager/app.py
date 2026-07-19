"""Compatibility entry point for the JEPA Site Manager modular layer.

This keeps the existing Tkinter authentication system working while exposing
an upgraded package-oriented structure for future modules.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = Path(__file__).resolve().parent

project_root_str = str(PROJECT_ROOT)
package_root_str = str(PACKAGE_ROOT)

if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)

if package_root_str not in sys.path:
    sys.path.append(package_root_str)

from auth.login import login_window
from database.db import init_db


def main() -> None:
    """Launch the JEPA Site Manager authentication flow as the main desktop entry point."""
    init_db()
    login_window()


if __name__ == "__main__":
    main()
