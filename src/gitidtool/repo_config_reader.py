from gitidtool.remote_config_entry import RemoteConfigEntry
from pathlib import Path
import regex
from dataclasses import dataclass
from gitidtool.repo_config_factory import RepoConfigFactory


@dataclass
class RepoConfigReader:
    factory: RepoConfigFactory

    def get_git_config_from_file(self, path: Path):
        self.factory.path = path
        is_in_user_section = False
        is_in_remote_section = False
        remote_name = None
        self.factory.remotes = []
        with open(path, "r") as file:
            for line in file:
                if line.startswith("[user]") and not is_in_user_section:
                    is_in_user_section = True
                    is_in_remote_section = False
                    continue
                if (
                    line.startswith("[remote")
                    and line.endswith("]\n")
                    and not is_in_remote_section
                ):
                    is_in_remote_section = True
                    is_in_user_section = False
                    remote_name = self._get_remote_name_from_line(line)
                    continue

                if is_in_user_section:
                    splits = line.split("=", 1)
                    key = splits[0].strip()
                    value = splits[1].strip()
                    match key:
                        case "name":
                            self.factory.name = value
                        case "email":
                            self.factory.email = value
                        case "signingkey":
                            self.factory.signing_key = value

                elif is_in_remote_section:
                    splits = line.split("=", 1)
                    key = splits[0].strip()
                    if key != "url":
                        continue
                    value = splits[1].strip()
                    if not value.startswith("https"):
                        self.factory.remotes.append(
                            RemoteConfigEntry(remote_name, value)
                        )
        return self.factory.create()

    def _get_remote_name_from_line(self, line: str):
        remote_name = regex.search(r'"[^"]*"', line).group(0)
        remote_name = remote_name.removeprefix('"').removesuffix('"')
        return remote_name
