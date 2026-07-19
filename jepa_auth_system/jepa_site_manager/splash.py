"""JEPA Site Manager splash wrapper.

The current splash experience is preserved and surfaced through the new
modular package for a gradual migration path.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ui.splash import splash_screen


def open_splash() -> None:
    """Display the existing splash screen from the new package namespace."""
    splash_screen()


if __name__ == "__main__":
    open_splash()
