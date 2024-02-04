import subprocess
import regex
from dataclasses import dataclass
from gitidtool.gpg_key_entry import GpgKeyEntry
from gitidtool.gpg_key_entry_factory import GpgKeyEntryFactory


@dataclass
class GpgKeyEntryReader:
    factory: GpgKeyEntryFactory

    def get_gpg_config(self):
        config_entries = list[GpgKeyEntry]()
        output = self._get_cmd_output()
        for line in output.splitlines():
            if line.startswith("pub"):
                self.factory.public_key = self._get_signing_key_from_line(line)
                continue
            if line.startswith("uid"):
                self.factory.name = self._get_name_from_line(line)
                self.factory.email = self._get_email_from_line(line)
                config_entries.append(self.factory.create())
                continue

        return config_entries

    def _get_cmd_output(self):
        output = subprocess.run(
            ["gpg", "--list-keys", "--keyid-format=long"],
            capture_output=True,
            check=True,
        )
        return output.stdout.decode()

    def _get_signing_key_from_line(self, line: str):
        value = regex.search(r"(?<=\/)\w+", line).group(0)
        return value

    def _get_name_from_line(self, line: str):
        value = regex.search(r"(?<=\] ).+(?= \<)", line).group(0)
        return value

    def _get_email_from_line(self, line: str):
        value = regex.search(r"(?<=\<).+(?=\>)", line).group(0)
        return value
