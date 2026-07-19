import unittest

import dashboard.admin_dashboard as admin_module


class AdminLiveMonitorTests(unittest.TestCase):
    def test_summarize_live_events_groups_registrations_and_logins(self):
        rows = [
            {"action": "Registration", "username": "newuser", "details": "New account", "ip_address": "192.168.1.10"},
            {"action": "Login Attempt", "username": "newuser", "details": "Successful login", "ip_address": "192.168.1.10"},
        ]

        summary = admin_module.summarize_live_events(rows)

        self.assertEqual(summary["registrations"], 1)
        self.assertEqual(summary["logins"], 1)
        self.assertIn("newuser", summary["latest"])

    def test_format_live_event_row_adds_device_context(self):
        row = {"timestamp": "2026-06-11 12:30:00", "username": "alice", "action": "Registration", "details": "New account", "ip_address": "10.0.0.5"}

        formatted = admin_module.format_live_event_row(row)

        self.assertIn("alice", formatted["label"])
        self.assertIn("10.0.0.5", formatted["label"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
