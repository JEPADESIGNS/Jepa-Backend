"""Role definitions and permission metadata for JEPA Site Manager."""

ROLE_LABELS = {
    "super_admin": "Super Admin",
    "admin": "Admin",
    "contractor": "Contractor",
    "project_manager": "Project Manager",
    "site_engineer": "Site Engineer",
    "store_keeper": "Store Keeper",
    "equipment_officer": "Equipment Officer",
    "client": "Client",
    "consultant": "Consultant",
}

# Centralized user roles catalog - all available registration roles
USER_ROLES = ROLE_LABELS.copy()

ROLE_ALIASES = {
    "superadmin": "super_admin",
    "projectmanager": "project_manager",
    "project_manager": "project_manager",
    "contractor": "contractor",
    "consultant": "consultant",
    "manager": "project_manager",
    "staff": "site_engineer",
    "user": "client",
}

MODULE_DEFINITIONS = {
    "overview": {
        "label": "Dashboard",
        "description": "Role-specific attention center with alerts, priorities and quick actions.",
    },
    "projects": {
        "label": "Projects",
        "description": "Project workspaces and delivery operations.",
    },
    "reports": {
        "label": "Reports",
        "description": "Daily reports, compliance tracking and review workflows.",
    },
    "materials": {
        "label": "Materials",
        "description": "Inventory, requests, and material usage tracking.",
    },
    "workforce": {
        "label": "Workforce",
        "description": "Attendance, crew deployment and site staffing.",
    },
    "equipment": {
        "label": "Equipment",
        "description": "Plant, assets and equipment readiness.",
    },
    "documents": {
        "label": "Documents",
        "description": "Drawings, BOQs, contracts, permits, reports and site photos.",
    },
    "issues": {
        "label": "Issues",
        "description": "Delay, safety, quality, materials, equipment and client concerns.",
    },
    "notifications": {
        "label": "Notifications",
        "description": "Alerts, reminders and operational messages.",
    },
    "administration": {
        "label": "Administration",
        "description": "System settings, user access and audit log management.",
    },
}

MODULE_ORDER = [
    "overview",
    "projects",
    "reports",
    "materials",
    "workforce",
    "equipment",
    "documents",
    "issues",
    "notifications",
    "administration",
]

ROLE_ACCESS = {
    "super_admin": set(MODULE_ORDER),
    "admin": {
        "overview",
        "projects",
        "reports",
        "materials",
        "workforce",
        "equipment",
        "documents",
        "issues",
        "notifications",
        "administration",
    },
    "contractor": {
        "overview",
        "projects",
        "reports",
        "materials",
        "workforce",
        "equipment",
        "documents",
        "issues",
        "notifications",
    },
    "project_manager": {
        "overview",
        "projects",
        "reports",
        "materials",
        "workforce",
        "documents",
        "issues",
        "notifications",
    },
    "site_engineer": {
        "overview",
        "projects",
        "reports",
        "materials",
        "workforce",
        "documents",
        "issues",
    },
    "store_keeper": {
        "overview",
        "projects",
        "materials",
        "documents",
        "issues",
    },
    "equipment_officer": {
        "overview",
        "projects",
        "equipment",
        "documents",
        "issues",
    },
    "client": {
        "overview",
        "projects",
        "reports",
        "documents",
        "issues",
    },
    "consultant": {
        "overview",
        "projects",
        "reports",
        "documents",
        "issues",
    },
}

ROLE_DEFAULT_LANDING = {
    "super_admin": "overview",
    "admin": "overview",
    "contractor": "overview",
    "project_manager": "overview",
    "site_engineer": "overview",
    "store_keeper": "overview",
    "equipment_officer": "overview",
    "client": "overview",
    "consultant": "overview",
}

ENTITY_HIERARCHY = ["company", "project", "site", "operation"]

DAILY_COMPLIANCE_KEYS = [
    "active_projects",
    "reports_submitted_today",
    "missing_reports",
    "compliance_percentage",
]


def normalize_role(role: str | None) -> str:
    value = (role or "client").strip().lower().replace(" ", "_")
    return ROLE_ALIASES.get(value, value)


def get_role_label(role: str | None) -> str:
    normalized = normalize_role(role)
    return ROLE_LABELS.get(normalized, normalized.replace("_", " ").title())


def get_module_label(module_name: str) -> str:
    return MODULE_DEFINITIONS.get(module_name, {}).get("label", module_name.replace("_", " ").title())


def get_default_landing_module(role: str | None) -> str:
    return ROLE_DEFAULT_LANDING.get(normalize_role(role), "overview")


def get_site_manager_actions() -> list[tuple[str, str]]:
    return [(MODULE_DEFINITIONS[module]["label"], module) for module in MODULE_ORDER if module in MODULE_DEFINITIONS]


def get_accessible_modules(role: str | None) -> set[str]:
    return set(ROLE_ACCESS.get(normalize_role(role), ROLE_ACCESS.get("client", set())))


def get_daily_report_compliance_keys() -> list[str]:
    return list(DAILY_COMPLIANCE_KEYS)
