import unittest
from unittest import mock

import auth.login as login_module


class FakeWidget:
    def pack(self, *args, **kwargs):
        return None

    def config(self, *args, **kwargs):
        return None


class FakeLabel(FakeWidget):
    instances = []

    def __init__(self, *args, **kwargs):
        self.text = kwargs.get("text", args[1] if len(args) > 1 else "")
        self.kwargs = kwargs
        self.bindings = {}
        FakeLabel.instances.append(self)

    def bind(self, event, callback):
        self.bindings[event] = callback


class FakeButton(FakeWidget):
    def __init__(self, *args, **kwargs):
        self.command = kwargs.get("command")


class FakeEntry(FakeWidget):
    def __init__(self, *args, **kwargs):
        self.textvariable = kwargs.get("textvariable")

    def focus_set(self):
        return None


class FakeStringVar:
    def __init__(self, *args, **kwargs):
        self.value = kwargs.get("value", "")

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class FakeTk:
    def __init__(self):
        self.children = []

    def title(self, *args, **kwargs):
        return None

    def geometry(self, *args, **kwargs):
        return None

    def resizable(self, *args, **kwargs):
        return None

    def configure(self, *args, **kwargs):
        return None

    def bind_all(self, *args, **kwargs):
        return None

    def destroy(self):
        return None

    def iconbitmap(self, *args, **kwargs):
        return None


class LoginForgotLinkTests(unittest.TestCase):
    def tearDown(self):
        FakeLabel.instances.clear()

    def test_forgot_password_label_opens_recovery_window(self):
        with mock.patch.object(login_module.tk, "Tk", return_value=FakeTk()), \
             mock.patch.object(login_module.tk, "Label", FakeLabel), \
             mock.patch.object(login_module.tk, "Button", FakeButton), \
             mock.patch.object(login_module.tk, "Entry", FakeEntry), \
             mock.patch.object(login_module.tk, "StringVar", FakeStringVar), \
             mock.patch.object(login_module, "password_entry", return_value=None), \
             mock.patch.object(login_module, "status_label", return_value=FakeWidget()), \
             mock.patch("auth.forgot_password.open_forgot_password") as open_forgot_password:

            login_module.login_window()

            forgot_label = next(
                (item for item in FakeLabel.instances if item.text == "Forgot your password?"),
                None,
            )

            self.assertIsNotNone(forgot_label, "Forgot password label should be created")
            self.assertIn("<Button-1>", forgot_label.bindings,
                          "Forgot password label should be clickable")

            forgot_label.bindings["<Button-1>"](None)

            open_forgot_password.assert_called_once()


if __name__ == "__main__":
    unittest.main(verbosity=2)
