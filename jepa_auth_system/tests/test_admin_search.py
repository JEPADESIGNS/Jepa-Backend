import unittest

import dashboard.admin_dashboard as admin_module


class AdminSearchTests(unittest.TestCase):
    def test_filter_matches_user_fields(self):
        rows = [
            {"id": 1, "username": "alice", "email": "alice@example.com", "phone": "+256700111111", "full_name": "Alice Smith"},
            {"id": 2, "username": "bob", "email": "bob@example.com", "phone": "+256700222222", "full_name": "Robert Brown"},
        ]

        filtered = admin_module.filter_users(rows, "bob")

        self.assertEqual([item["id"] for item in filtered], [2])

    def test_filter_is_case_insensitive(self):
        rows = [
            {"id": 1, "username": "alice", "email": "alice@example.com", "phone": "+256700111111", "full_name": "Alice Smith"},
        ]

        filtered = admin_module.filter_users(rows, "ALICE")

        self.assertEqual(len(filtered), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
