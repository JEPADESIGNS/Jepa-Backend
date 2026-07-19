import unittest

import dashboard.admin_dashboard as admin_module


class AdminLayoutHelpersTests(unittest.TestCase):
    def test_describe_selected_user_formats_summary(self):
        values = (7, 'alice', 'alice@example.com', '+256700000000', 'Alice Smith', 'USER', 'ACTIVE', 'Enabled')

        summary = admin_module.describe_selected_user(values)

        self.assertIn('alice', summary)
        self.assertIn('alice@example.com', summary)
        self.assertIn('ACTIVE', summary)

    def test_toggle_visibility_uses_visible_flag(self):
        visible = admin_module.toggle_panel_visibility(True)

        self.assertFalse(visible)


if __name__ == "__main__":
    unittest.main(verbosity=2)
