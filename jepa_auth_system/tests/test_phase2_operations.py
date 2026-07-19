import unittest

from dashboard import get_site_manager_actions


class Phase2OperationsTests(unittest.TestCase):
    def test_site_manager_actions_include_operations_modules(self):
        labels = [label for label, _ in get_site_manager_actions()]

        self.assertIn("Attendance", labels)
        self.assertIn("Equipment", labels)
        self.assertIn("BOQ & Costs", labels)
        self.assertIn("Analytics", labels)


if __name__ == '__main__':
    unittest.main(verbosity=2)
