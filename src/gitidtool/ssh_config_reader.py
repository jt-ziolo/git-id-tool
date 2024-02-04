from pathlib import Path
from dataclasses import dataclass
import regex
from gitidtool.ssh_config_entry import SshConfigEntry
from gitidtool.ssh_config_entry_factory import SshConfigEntryFactory


@dataclass
class SshConfigReader:
    factory: SshConfigEntryFactory

    def get_config_entries_from_file(
        self, path: Path = Path.home().joinpath(".ssh", "config")
    ):
        config_entries: list[SshConfigEntry] = []
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
                        self.factory.email = self.get_email_from_identity_file(value)
                        config_entries.append(self.factory.create_entry())
        return config_entries

    def get_email_from_identity_file(self, identity_file: Path):
        pub_path = Path(f"{identity_file}.pub").expanduser()
        content = ""
        with open(pub_path.resolve(), "r") as file:
            content = file.read()
        # From the public key content, get the email address
        return regex.search(r"\b\w*@\w*\.\w*\b", content).group(0).strip()
