"""
auth/security.py — bcrypt hashing and security utilities.
"""
import secrets
import bcrypt
import pyotp


# ── Password hashing ──────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    """Hash a plain-text password with bcrypt. Returns the hash as a UTF-8 string."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ── Security answer hashing ───────────────────────────────────────────────────

def hash_answer(answer: str) -> str:
    """Normalise and hash a security answer."""
    return hash_password(answer.strip().lower())


def verify_answer(answer: str, hashed: str) -> bool:
    return verify_password(answer.strip().lower(), hashed)


# ── Recovery code generation ──────────────────────────────────────────────────

def generate_recovery_code() -> str:
    """Return a unique, URL-safe, 32-character recovery code."""
    return secrets.token_urlsafe(24)


# ── Two-Factor Authentication (2FA) Helpers ────────────────────────────────────

def generate_totp_secret() -> str:
    """Generates a random base32 string for the user's authenticating device."""
    return pyotp.random_base32()


def get_totp_uri(username: str, secret: str) -> str:
    """Returns a standardized setup URI for registration QR codes."""
    return pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name="JEPA Workspace")


def verify_totp(secret: str, code: str) -> bool:
    """Validates the input 6-digit dynamic token code against the user secret."""
    if not secret:
        return False
    return pyotp.totp.TOTP(secret).verify(code.strip())


# ── Admin gate ────────────────────────────────────────────────────────────────

ADMIN_REGISTRATION_CODE = "ADMIN2026"


def is_valid_admin_code(code: str) -> bool:
    return secrets.compare_digest(code.strip(), ADMIN_REGISTRATION_CODE)