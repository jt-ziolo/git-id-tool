import unittest
from unittest.mock import PropertyMock, patch
from gitidtool.git_data import GitDataEntry
from gitidtool.gpg_data import GpgDataEntry


class TestExampleWithMocking(unittest.TestCase):
    def setUp(self):
        self.signingkey = "ABCDEFGHIJKLMNOP"
        self.gpg_entry = GpgDataEntry(self.signingkey, "gpg name", "gpg email")
        self.entry = GitDataEntry(
            "HOME/Example/Directories/RepoName/.git/config",
            "name",
            "email",
            self.signingkey,
            [self.gpg_entry],
        )
        # Management by test adapter
        patcher = patch(
            "gitidtool.git_data.GitDataEntry.name",
            new_callable=PropertyMock,
            return_value="From Managed Mock"
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_property(self):
        self.assertEqual(self.entry.repo_folder_name, "RepoName")
        with patch(
            "gitidtool.git_data.GitDataEntry.repo_folder_name",
            new_callable=PropertyMock,
        ) as mock_property:
            mock_property.return_value = "From Property Mock"
            self.assertEqual(self.entry.repo_folder_name, "From Property Mock")
        # Managed mock
        self.assertEqual(self.entry.name, "From Managed Mock")

    def test_method(self):
        self.assertEqual(
            self.entry.get_gpg_entry_matching_signing_key([self.gpg_entry]),
            self.gpg_entry,
        )
        with patch(
            "gitidtool.git_data.GitDataEntry.get_gpg_entry_matching_signing_key",
        ) as mock_method:
            mock_method.return_value = "From Method Mock"
            self.assertEqual(
                self.entry.get_gpg_entry_matching_signing_key([self.gpg_entry]),
                "From Method Mock",
            )
        # Managed mock
        self.assertEqual(self.entry.name, "From Managed Mock")


if __name__ == "__main__":
    unittest.main()
