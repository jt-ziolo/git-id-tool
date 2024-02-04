from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

import regex

from gitidtool.gpg_data import GpgDataEntry
from gitidtool.ssh_data import SshDataEntry


@dataclass(frozen=True)
class GitRemoteDataEntry:
    remote_name: str
    url: str

    @cached_property
    def hostname(self):
        return self.url.split("@", 1)[1].split(":", 1)[0]

    def get_ssh_entry_matching_hostname(self, ssh_config: list[SshDataEntry]):
        ssh_entries = [
            ssh_entry for ssh_entry in ssh_config if ssh_entry.hostname == self.hostname
        ]
        if len(ssh_entries) == 0:
            # no matching ssh host
            return None
        # the first entry is what matters
        return ssh_entries[0]

    def __hash__(self):
        return hash((self.remote_name, self.url))


@dataclass(frozen=True)
class GitDataEntry:
    path: str = ""
    name: str = ""
    email: str = ""
    signing_key: str = ""
    remotes: list[GitRemoteDataEntry] = field(default_factory=list)

    def get_gpg_entry_matching_signing_key(self, gpg_config: list[GpgDataEntry]):
        gpg_entries = [
            gpg_entry
            for gpg_entry in gpg_config
            if gpg_entry.public_key == self.signing_key
        ]
        if len(gpg_entries) == 0:
            # no matching key
            return None
        if len(gpg_entries) > 1:
            # invalid
            raise RuntimeError(
                f"Multiple gpg entries match the given signing key {self.signing_key}, which is not allowed."
            )
        # the first entry is what matters
        return gpg_entries[0]

    @cached_property
    def repo_folder_name(self):
        parts = Path(self.path).parts
        # get the third-to-last part, before "/.git/" and "/config"
        return parts[len(parts) - 3]


@dataclass
class GitDataEntryFactory:
    path: str = ""
    name: str = ""
    email: str = ""
    signing_key: str = ""
    remotes: list[GitRemoteDataEntry] = field(default_factory=list)

    def create(self):
        return GitDataEntry(
            self.path, self.name, self.email, self.signing_key, self.remotes
        )


@dataclass
class GitDataReader:
    factory: GitDataEntryFactory

    def get_git_config_from_file(self, path: Path):
        self.factory.path = path
        is_in_user_section = False
        is_in_remote_section = False
        remote_name = None
        self.factory.remotes = []
        with open(path, "r") as file:
            for line in file:
                if line.startswith("[user]") and not is_in_user_section:
                    is_in_user_section = True
                    is_in_remote_section = False
                    continue
                if (
                    line.startswith("[remote")
                    and line.endswith("]\n")
                    and not is_in_remote_section
                ):
                    is_in_remote_section = True
                    is_in_user_section = False
                    remote_name = self._get_remote_name_from_line(line)
                    continue

                if is_in_user_section:
                    splits = line.split("=", 1)
                    key = splits[0].strip()
                    value = splits[1].strip()
                    match key:
                        case "name":
                            self.factory.name = value
                        case "email":
                            self.factory.email = value
                        case "signingkey":
                            self.factory.signing_key = value

                elif is_in_remote_section:
                    splits = line.split("=", 1)
                    key = splits[0].strip()
                    if key != "url":
                        continue
                    value = splits[1].strip()
                    if not value.startswith("https"):
                        self.factory.remotes.append(
                            GitRemoteDataEntry(remote_name, value)
                        )
        return self.factory.create()

    def _get_remote_name_from_line(self, line: str):
        remote_name = regex.search(r'"[^"]*"', line).group(0)
        remote_name = remote_name.removeprefix('"').removesuffix('"')
        return remote_name
