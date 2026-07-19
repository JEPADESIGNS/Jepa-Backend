import unittest
from unittest import mock

import dashboard.profile as profile_module


class FakeFrame:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        self.tk = object()

    def pack(self, *args, **kwargs):
        return None


class FakeLabel:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs

    def pack(self, *args, **kwargs):
        return None

    def config(self, *args, **kwargs):
        return None


class FakeEntry:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs

    def pack(self, *args, **kwargs):
        return None


class FakeButton:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs

    def pack(self, *args, **kwargs):
        return None


class FakeNotebook:
    def __init__(self, *args, **kwargs):
        self.tabs = {}

    def add(self, child, text=None):
        self.tabs[text] = child

    def pack(self, *args, **kwargs):
        return None


class FakeToplevel:
    def __init__(self, *args, **kwargs):
        self.closed = False
        self.tk = object()

    def title(self, *args, **kwargs):
        return None

    def geometry(self, *args, **kwargs):
        return None

    def resizable(self, *args, **kwargs):
        return None

    def configure(self, *args, **kwargs):
        return None

    def grab_set(self):
        return None

    def destroy(self):
        self.closed = True


class FakeStringVar:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class ProfileEditorTabsTests(unittest.TestCase):
    def test_profile_editor_creates_photo_tab(self):
        fake_notebook = FakeNotebook()

        fake_row = {"full_name": "Jane", "phone": "+256700000000", "gender": "Female", "dob": "1999-01-01", "bio": ""}

        with mock.patch.object(profile_module.tk, "Toplevel", return_value=FakeToplevel()), \
             mock.patch.object(profile_module.tk, "Frame", FakeFrame), \
             mock.patch.object(profile_module.tk, "Label", FakeLabel), \
             mock.patch.object(profile_module.tk, "Entry", FakeEntry), \
             mock.patch.object(profile_module.tk, "Button", FakeButton), \
             mock.patch.object(profile_module.tk, "StringVar", FakeStringVar), \
             mock.patch.object(profile_module, "status_label", return_value=FakeLabel()), \
             mock.patch("dashboard.profile.ttk.Notebook", return_value=fake_notebook), \
             mock.patch("dashboard.profile.get_connection") as get_connection:
            conn = mock.MagicMock()
            conn.__enter__.return_value.execute.return_value.fetchone.return_value = fake_row
            get_connection.return_value = conn

            profile_module.open_profile_editor(mock.Mock(), 7, "jane", {"bg": "#0F172A", "fg": "#F8FAFC", "lbl_sub": "#94A3B8", "input_bg": "#334155", "accent": "#0EA5E9", "btn_sec": "#1E293B", "btn_sec_fg": "#94A3B8", "error": "#EF4444", "success": "#10B981"}, None)

        self.assertIn("Profile", fake_notebook.tabs)
        self.assertIn("Photo", fake_notebook.tabs)


if __name__ == "__main__":
    unittest.main(verbosity=2)
