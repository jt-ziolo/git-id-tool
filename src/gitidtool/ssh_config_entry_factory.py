from gitidtool.ssh_config_entry import SshConfigEntry


class SshConfigEntryFactory:
    email: str
    hostname: str

    def __init__(self):
        pass

    def create_entry(self):
        return SshConfigEntry(self.hostname, self.email)
