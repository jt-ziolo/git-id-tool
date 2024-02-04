from gitidtool.ssh_config_entry import SshConfigEntry


class SshConfigEntryFactory:
    email: str
    hostname: str
    identity_file_path: str

    def create(self):
        return SshConfigEntry(self.hostname, self.email, self.identity_file_path)
