"""
utils/csv_export.py — Export users table to CSV.
"""
import csv
from pathlib import Path
from database.db import get_connection


def export_users_to_csv(dest_path: Path | None = None) -> Path:
    """
    Write all users to a CSV file and return the path.
    Defaults to ~/Desktop/JEPA_Users.csv.
    """
    if dest_path is None:
        dest_path = Path.home() / "Desktop" / "JEPA_Users.csv"

    dest_path.parent.mkdir(parents=True, exist_ok=True)

    headers = [
        "id", "username", "email", "phone", "full_name",
        "country_code", "gender", "dob", "role", "status",
        "theme", "created_at",
    ]

    with get_connection() as conn:
        rows = conn.execute(
            f"SELECT {', '.join(headers)} FROM users ORDER BY id"
        ).fetchall()

    with open(dest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([h.upper() for h in headers])
        writer.writerows(rows)

    return dest_path
