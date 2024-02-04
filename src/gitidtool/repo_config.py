from functools import cached_property
from gitidtool.gpg_key_entry import GpgKeyEntry
from gitidtool.remote_config_entry import RemoteConfigEntry
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class RepoConfig:
    path: str = ""
    name: str = ""
    email: str = ""
    signing_key: str = ""
    remotes: list[RemoteConfigEntry] = field(default_factory=list)

    def get_gpg_entry_matching_signing_key(self, gpg_config: list[GpgKeyEntry]):
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
