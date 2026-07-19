"""Central permission helpers for the JEPA Site Manager platform."""

from jepa_site_manager.auth.roles import (
    normalize_role,
    get_module_label,
    get_role_label,
    get_site_manager_actions,
    get_accessible_modules,
    get_default_landing_module,
)


def can_access_module(role: str | None, module_name: str) -> bool:
    """Return True when the role is permitted to open the given module."""
    return (module_name or "").lower() in get_accessible_modules(role)


def can_perform_action(role: str | None, module_name: str) -> bool:
    """Return True when the role may perform actions in the given module."""
    return can_access_module(role, module_name)


def get_accessible_site_manager_actions(role: str | None) -> list[tuple[str, str]]:
    """Return only the module actions this user can open."""
    allowed = get_accessible_modules(role)
    return [(get_module_label(name), name) for name, _ in get_site_manager_actions() if name in allowed]


def get_default_dashboard_module(role: str | None) -> str:
    """Return the default module landing page for the role."""
    return get_default_landing_module(role)


def get_navigation_items(role: str | None) -> list[tuple[str, str]]:
    """Return sidebar navigation items for a role."""
    return get_accessible_site_manager_actions(role)


def get_role_title(role: str | None) -> str:
    """Return the human-readable role title."""
    return get_role_label(role)
