"""
ui/themes.py — Light / Dark theme manager and shared style constants.
"""

THEMES: dict[str, dict] = {
    "dark": {
        "bg":           "#10263C",
        "panel":        "#17314A",
        "panel2":       "#0F172A",
        "fg":           "#EAF4FF",
        "lbl_sub":      "#A9C7E2",
        "input_bg":     "#1F3A58",
        "border":       "#2A5A8C",
        "accent":       "#E05C1A",
        "accent_hover": "#F0A500",
        "success":      "#10B981",
        "error":        "#EF4444",
        "warning":      "#F59E0B",
        "btn_sec":      "#1E3A5F",
        "btn_sec_fg":   "#EAF4FF",
        "tag_active":   "#10B981",
        "tag_suspended":"#EF4444",
    },
    "light": {
        "bg":           "#F8FAFC",
        "panel":        "#FFFFFF",
        "panel2":       "#F1F5F9",
        "fg":           "#0F172A",
        "lbl_sub":      "#64748B",
        "input_bg":     "#F1F5F9",
        "border":       "#CBD5E1",
        "accent":       "#0284C7",
        "accent_hover": "#0369A1",
        "success":      "#059669",
        "error":        "#DC2626",
        "warning":      "#D97706",
        "btn_sec":      "#E2E8F0",
        "btn_sec_fg":   "#475569",
        "tag_active":   "#059669",
        "tag_suspended":"#DC2626",
    },
}


def get_theme(name: str) -> dict:
    """Return the theme dict for name, defaulting to 'dark'."""
    return THEMES.get(name, THEMES["dark"])


# ── Typography constants ───────────────────────────────────────────────────────

FONT_FAMILY = "Segoe UI"

FONTS = {
    "brand":    (FONT_FAMILY, 10,  "bold"),
    "h1":       (FONT_FAMILY, 18, "bold"),
    "h2":       (FONT_FAMILY, 14, "bold"),
    "h3":       (FONT_FAMILY, 12, "bold"),
    "body":     (FONT_FAMILY, 11),
    "body_bold":(FONT_FAMILY, 11, "bold"),
    "small":    (FONT_FAMILY, 9),
    "small_bold":(FONT_FAMILY, 9, "bold"),
    "label":    (FONT_FAMILY, 8,  "bold"),
    "mono":     ("Consolas",  10),
}

# ── Layout constants ───────────────────────────────────────────────────────────

PAD_H   = 45   # Horizontal padding inside windows
PAD_V   = 8    # Vertical padding between form rows
IPADY   = 5    # Inner vertical padding for entry widgets
RADIUS  = 6    # Conceptual corner radius (applied where tk supports it)


# ── Country code reference list ────────────────────────────────────────────────

COUNTRY_CODES: dict[str, str] = {
    "Uganda":        "+256",
    "Kenya":         "+254",
    "Tanzania":      "+255",
    "Rwanda":        "+250",
    "Nigeria":       "+234",
    "South Africa":  "+27",
    "United States": "+1",
    "United Kingdom":"+44",
    "United Arab Emirates": "+971",
    "India":         "+91",
    "Canada":        "+1",
    "Australia":     "+61",
    "Germany":       "+49",
    "France":        "+33",
    "China":         "+86",
    "Japan":         "+81",
    "Brazil":        "+55",
}

COUNTRY_LIST = [f"{name} ({code})" for name, code in sorted(COUNTRY_CODES.items())]

SECURITY_QUESTIONS = [
    "What was the name of your first pet?",
    "What is the name of the city where you were born?",
    "What is your mother's maiden name?",
    "What was the name of your primary school?",
    "What was the make of your first car?",
    "What is your oldest sibling's middle name?",
    "What street did you grow up on?",
]
