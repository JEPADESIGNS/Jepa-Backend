# JEPA Authentication & User Management System

A secure, modular desktop authentication system built with Python and Tkinter.

## Features

- **bcrypt password hashing** — replaces the old SHA-256 approach
- **Flexible login** — accepts username, email, or phone number
- **Full registration** with password strength indicator, security question, and auto-generated recovery code
- **Password recovery** via security question or recovery code
- **Light / Dark theme** — persisted per user
- **User dashboard** — view and edit profile, change password
- **Admin dashboard** — view all users, suspend/reinstate, reset passwords, promote to admin, view per-user activity logs, export CSV
- **Structured activity logging** — every key action is recorded with timestamp, user ID, and details

## Project Structure

```
jepa_auth_system/
├── main.py                    # Entry point
├── requirements.txt
├── assets/
│   ├── JEPA DESIGN LOGO.png
│   ├── app_icon.ico
│   └── default_avatar.png
├── database/
│   ├── db.py                  # Connection, init, migrations
│   └── schema.sql             # Full SQL schema
├── auth/
│   ├── login.py               # Login window
│   ├── register.py            # Registration form
│   ├── forgot_password.py     # Recovery workflows
│   ├── security.py            # bcrypt hashing, recovery codes
│   └── validators.py          # Input validation, password strength
├── ui/
│   ├── splash.py              # Animated splash screen
│   ├── themes.py              # Light/Dark theme manager + constants
│   └── components.py         # Reusable Tkinter widgets
├── dashboard/
│   ├── user_dashboard.py      # User account dashboard
│   ├── profile.py             # Profile editing window
│   ├── change_password.py     # Password change dialog
│   └── admin_dashboard.py     # Admin management panel
└── utils/
    ├── logger.py              # Activity logging helpers
    └── csv_export.py          # Export users to CSV
```

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
python main.py
```

## Default Admin Code

`ADMIN2026` — change this in `auth/security.py` before deployment.

## Data Storage

All persistent data is stored under `~/.jepa_auth/`:
- `data/jepa_auth.db` — SQLite database
- `profile_pics/` — uploaded avatar images

## Security Notes

- Passwords are hashed with **bcrypt** (work factor 12)
- Security question answers are also bcrypt-hashed
- Recovery codes are 32-character cryptographically random tokens
- Account status (`active` / `suspended`) is enforced at every login
- All admin actions are logged with the admin's user ID
