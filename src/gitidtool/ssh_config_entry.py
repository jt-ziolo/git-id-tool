from dataclasses import dataclass


@dataclass
class SshConfigEntry:
    hostname: str
    email: str
