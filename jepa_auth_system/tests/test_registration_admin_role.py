import unittest

from auth.register import validate_registration_role


class RegistrationRoleTests(unittest.TestCase):
    def test_admin_role_does_not_require_admin_code(self):
        self.assertIsNone(validate_registration_role("admin", ""))


if __name__ == "__main__":
    unittest.main()
