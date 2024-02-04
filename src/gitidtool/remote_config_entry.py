from dataclasses import dataclass
from functools import cached_property

from gitidtool.ssh_config_entry import SshConfigEntry


@dataclass
class RemoteConfigEntry:
    remote_name: str
    url: str

    @cached_property
    def hostname(self):
        return self.url.split("@", 1)[1].split(":", 1)[0]

    def get_ssh_entry_matching_hostname(self, ssh_config: list[SshConfigEntry]):
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
