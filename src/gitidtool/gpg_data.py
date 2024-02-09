import subprocess
from dataclasses import dataclass

import regex


@dataclass(frozen=True)
class GpgDataEntry:
    public_key: str
    name: str
    email: str


class GpgDataEntryFactory:
    public_key: str
    name: str
    email: str

    def create(self):
        return GpgDataEntry(self.public_key, self.name, self.email)


@dataclass
class GpgDataReader:
    factory: GpgDataEntryFactory

    def get_gpg_config(self):
        config_entries = list[GpgDataEntry]()
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
            ["gpg", "--list-secret-keys", "--keyid-format=long"],
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
