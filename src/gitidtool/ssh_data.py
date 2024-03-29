from dataclasses import dataclass
from pathlib import Path

import regex


@dataclass(frozen=True)
class SshDataEntry:
    hostname: str
    email: str
    identity_file_path: str


class SshDataEntryFactory:
    email: str
    hostname: str
    identity_file_path: str

    def create(self):
        return SshDataEntry(self.hostname, self.email, self.identity_file_path)


@dataclass
class SshDataReader:
    factory: SshDataEntryFactory

    def get_config_entries_from_file(
        self, path: Path = Path.home().joinpath(".ssh", "config")
    ):
        config_entries: list[SshDataEntry] = []
        with open(path, "r") as file:
            for line in file:
                # Remove whitespace
                line_stripped = line.strip()
                # Skip the line if it is blank
                if line_stripped == "":
                    continue
                # Get the key/value pair on the line
                [key, value] = line_stripped.split()
                # switch on the key
                match key:
                    case "Host":
                        self.factory.hostname = value
                    case "IdentityFile":
                        self.factory.identity_file_path = value
                        self.factory.email = self.get_email_from_identity_file(value)
                        config_entries.append(self.factory.create())
        return config_entries

    def get_email_from_identity_file(self, identity_file: Path):
        pub_path = Path(f"{identity_file}.pub").expanduser()
        content = ""
        with open(pub_path.resolve(), "r") as file:
            content = file.read()
        # From the public key content, get the email address
        return regex.search(r"\b\w*@\w*\.\w*\b", content).group(0).strip()
