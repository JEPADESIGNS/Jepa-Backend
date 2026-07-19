"""Theme support adapter for the modular JEPA Site Manager package."""

from ui.themes import FONTS, get_theme


def get_palette(name: str = "dark") -> dict:
    """Return a theme palette using the existing Tkinter theme helpers."""
    return get_theme(name)


def get_fonts() -> dict:
    """Return the shared font dictionary used by the existing UI."""
    return FONTS
