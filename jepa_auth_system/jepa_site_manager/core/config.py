"""Shared configuration for JEPA Site Manager."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIR = PROJECT_ROOT / "assets"
DATABASE_DIR = PROJECT_ROOT / "database"
USER_DATA_DIR = Path.home() / ".jepa_auth"
DB_PATH = USER_DATA_DIR / "data" / "jepa_auth.db"

ROLE_ORDER = [
    "Super Admin",
    "Admin",
    "Project Manager",
    "Site Engineer",
    "Store Keeper",
    "Client",
]
