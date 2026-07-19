"""
auth/validators.py — Input validation and password strength checks.
"""
import re


# ── Password strength ─────────────────────────────────────────────────────────

PASSWORD_PATTERN = re.compile(
    r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'
)

PASSWORD_HINT = (
    "Password must be at least 8 characters and include: "
    "an uppercase letter, a lowercase letter, a digit, "
    "and a special character (@  $  !  %  *  ?  &)."
)


def is_strong_password(pw: str) -> bool:
    return bool(PASSWORD_PATTERN.match(pw))


def password_strength_label(pw: str) -> tuple[str, str]:
    """Return (label, colour) for a live strength indicator."""
    if len(pw) == 0:
        return ("", "#94A3B8")
    score = sum([
        len(pw) >= 8,
        bool(re.search(r'[A-Z]', pw)),
        bool(re.search(r'[a-z]', pw)),
        bool(re.search(r'\d', pw)),
        bool(re.search(r'[@$!%*?&]', pw)),
    ])
    if score <= 2:
        return ("Weak", "#EF4444")
    elif score == 3:
        return ("Fair", "#F59E0B")
    elif score == 4:
        return ("Good", "#3B82F6")
    else:
        return ("Strong", "#10B981")


# ── Field validators ──────────────────────────────────────────────────────────

def is_valid_email(email: str) -> bool:
    return bool(re.match(r'^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$', email.strip()))


def is_valid_username(username: str) -> bool:
    """3-30 chars, letters, digits, underscores, hyphens only."""
    return bool(re.match(r'^[\w-]{3,30}$', username.strip()))


def is_valid_phone(phone: str) -> bool:
    """Digits only, 7-15 chars (excluding country code prefix)."""
    return bool(re.match(r'^\d{7,15}$', phone.strip()))


def normalise_username(username: str) -> str:
    return username.strip().lower()


def normalise_email(email: str) -> str:
    return email.strip().lower()
