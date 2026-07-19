import unittest

from jepa_site_manager.core import hub


class HubRoleWorkspaceTests(unittest.TestCase):
    def test_role_workspace_summary_contains_engineer_focus(self):
        summary = hub.get_role_workspace_summary("site_engineer")

        self.assertIn("Today’s site priorities", summary["headline"])
        self.assertIn("Pending inspections", summary["focus_items"])
        self.assertIn("Material requests", summary["focus_items"])

    def test_role_workspace_summary_contains_client_focus(self):
        summary = hub.get_role_workspace_summary("client")

        self.assertIn("Project visibility", summary["headline"])
        self.assertIn("Latest site photos", summary["focus_items"])
        self.assertIn("Upcoming milestones", summary["focus_items"])

    def test_role_workspace_summary_includes_role_specific_actions(self):
        site_summary = hub.get_role_workspace_summary("site_engineer")
        client_summary = hub.get_role_workspace_summary("client")

        self.assertIn("Field checklist", site_summary["recommended_actions"])
        self.assertIn("Site reports", client_summary["recommended_actions"])


if __name__ == "__main__":
    unittest.main()
