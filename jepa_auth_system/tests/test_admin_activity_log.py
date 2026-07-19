import unittest

import dashboard.admin_dashboard as admin_module


class AdminActivityLogTests(unittest.TestCase):
    def test_format_activity_rows_returns_summary(self):
        rows = [
            {"timestamp": "2026-06-11 10:00:00", "username": "alice", "action": "Login Attempt", "details": "Successful login"},
            {"timestamp": "2026-06-11 11:00:00", "username": "bob", "action": "Password Reset", "details": None},
        ]

        formatted = admin_module.format_activity_rows(rows)

        self.assertEqual(formatted[0]["username"], "alice")
        self.assertIn("Login Attempt", formatted[0]["summary"])
        self.assertIn("Successful login", formatted[0]["summary"])

    def test_filter_activity_logs_matches_username(self):
        rows = [
            {"username": "alice", "action": "Login Attempt", "details": ""},
            {"username": "bob", "action": "Password Reset", "details": ""},
        ]

        filtered = admin_module.filter_activity_logs(rows, "bob")

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["username"], "bob")


if __name__ == "__main__":
    unittest.main(verbosity=2)
