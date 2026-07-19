import unittest

import auth.register as register_module
import dashboard
from jepa_site_manager.auth import roles as role_module


class RoleRestrictionTests(unittest.TestCase):
    def test_registration_roles_include_all_supported_roles(self):
        """Verify registration includes all 9 supported roles from centralized source."""
        expected_roles = {"super_admin", "admin", "contractor", "project_manager", "site_engineer", "store_keeper", "equipment_officer", "client", "consultant"}
        actual_roles = set(role for label, role in register_module.ROLE_CHOICES)
        self.assertEqual(actual_roles, expected_roles)

    def test_role_catalog_contains_all_supported_roles(self):
        """Verify USER_ROLES includes all 9 supported roles."""
        expected_roles = {"super_admin", "admin", "contractor", "project_manager", "site_engineer", "store_keeper", "equipment_officer", "client", "consultant"}
        self.assertEqual(set(role_module.USER_ROLES.keys()), expected_roles)

    def test_dashboard_access_map_includes_all_roles(self):
        """Verify ROLE_ACCESS includes all 9 supported roles."""
        expected_roles = {"super_admin", "admin", "contractor", "project_manager", "site_engineer", "store_keeper", "equipment_officer", "client", "consultant"}
        self.assertEqual(set(dashboard.ROLE_ACCESS.keys()), expected_roles)


if __name__ == "__main__":
    unittest.main()
