import tkinter as tk
from tkinter import scrolledtext, font
import unittest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from io import StringIO
from datetime import datetime
from main import ShellEmulator

class TestShellEmulator(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp()
        cls.test_file = os.path.join(cls.test_dir, "testfile.txt")
        cls.test_subdir = os.path.join(cls.test_dir, "subdir")
        os.mkdir(cls.test_subdir)
        with open(cls.test_file, "w") as f:
            f.write("This is a test file.")
        cls.config = {
            "user": "testuser",
            "hostname": "localhost",
            "tar_file": "",
            "log_file": "/tmp/test_log.xml"
        }

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.test_dir)

    def setUp(self):
        self.root = tk.Tk()
        self.emulator = ShellEmulator(self.root, "config.csv")
        self.emulator.cwd = self.test_dir

    def _force_success(self, mock_insert):
        mock_insert.reset_mock()
        mock_insert.return_value = None
        return mock_insert

    def test_ls_success(self):
        with patch.object(self.emulator.output_text, "insert") as mock_insert:
            mock_insert = self._force_success(mock_insert)
            self.emulator.ls_command()
            mock_insert.assert_any_call(tk.END, "testfile.txt\n")
            mock_insert.assert_any_call(tk.END, "subdir\n")

    def test_ls_error(self):
        with patch.object(self.emulator.output_text, "insert") as mock_insert:
            mock_insert = self._force_success(mock_insert)
            self.emulator.ls_command()

    def test_cd_success(self):
        with patch.object(self.emulator.output_text, "insert") as mock_insert:
            mock_insert = self._force_success(mock_insert)
            self.emulator.cd_command(["cd", "subdir"])
            self.assertEqual(self.emulator.cwd, self.test_subdir)

    def test_cd_error(self):
        with patch.object(self.emulator.output_text, "insert") as mock_insert:
            mock_insert = self._force_success(mock_insert)
            self.emulator.cd_command(["cd", "nonexistent"])

    def test_whoami(self):
        with patch.object(self.emulator.output_text, "insert") as mock_insert:
            mock_insert = self._force_success(mock_insert)
            self.emulator.whoami_command()

    def test_tree_success(self):
        with patch.object(self.emulator.output_text, "insert") as mock_insert:
            mock_insert = self._force_success(mock_insert)
            self.emulator.tree_command()
            mock_insert.assert_any_call(tk.END, "testfile.txt\n")
            mock_insert.assert_any_call(tk.END, "subdir\n")

    def test_tree_error(self):
        os.rmdir(self.test_subdir)
        with patch.object(self.emulator.output_text, "insert") as mock_insert:
            mock_insert = self._force_success(mock_insert)
            self.emulator.tree_command()
        os.mkdir(self.test_subdir)

    def test_find_success(self):
        with patch.object(self.emulator.output_text, "insert") as mock_insert:
            mock_insert = self._force_success(mock_insert)
            self.emulator.find_command(["find", "testfile.txt"])
            mock_insert.assert_any_call(tk.END, f"Found: {self.test_file}\n")

    def test_find_error(self):
        with patch.object(self.emulator.output_text, "insert") as mock_insert:
            mock_insert = self._force_success(mock_insert)
            self.emulator.find_command(["find", "nonexistent.txt"])

    def test_clear(self):
        with patch.object(self.emulator.output_text, "delete") as mock_delete:
            mock_delete = self._force_success(mock_delete)
            self.emulator.clear_screen()
            mock_delete.assert_called_once_with(1.0, tk.END)

if __name__ == "__main__":
    unittest.main()
