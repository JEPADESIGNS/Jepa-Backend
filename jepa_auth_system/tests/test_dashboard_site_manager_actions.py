import unittest
from unittest.mock import patch

from dashboard import get_site_manager_actions, open_site_manager_module, get_accessible_site_manager_actions


class SiteManagerActionTest(unittest.TestCase):
    def test_site_manager_actions_include_workflow_links(self):
        actions = get_site_manager_actions()

        labels = [label for label, _ in actions]

        self.assertIn("Daily Brief", labels)
        self.assertIn("Project Workspace", labels)
        self.assertIn("Site Reports", labels)
        self.assertIn("Store & Materials", labels)

    def test_role_based_access_limits_client_view(self):
        actions = get_accessible_site_manager_actions("client")
        labels = [label for label, _ in actions]

        self.assertIn("Daily Brief", labels)
        self.assertIn("Site Reports", labels)
        self.assertNotIn("Project Workspace", labels)

    def test_open_site_manager_module_uses_project_view(self):
        with patch("jepa_site_manager.projects.project_view.open_project_manager", return_value=None) as open_project:
            open_site_manager_module(None, "projects")

        open_project.assert_called_once_with(None)

    def test_open_site_manager_module_uses_role_for_overview(self):
        with patch("jepa_site_manager.core.hub.open_site_manager_hub", return_value=None) as open_hub:
            open_site_manager_module(None, "overview", "site_engineer")

        open_hub.assert_called_once_with(None, role="site_engineer")


if __name__ == "__main__":
    unittest.main()
