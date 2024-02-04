from dataclasses import dataclass


@dataclass(frozen=True)
class SshConfigEntry:
    hostname: str
    email: str
    identity_file_path: str
