from gitidtool.remote_config_entry import RemoteConfigEntry
from dataclasses import dataclass, field
from gitidtool.repo_config import RepoConfig


@dataclass
class RepoConfigFactory:
    path: str = ""
    name: str = ""
    email: str = ""
    signing_key: str = ""
    remotes: list[RemoteConfigEntry] = field(default_factory=list)

    def create(self):
        return RepoConfig(
            self.path, self.name, self.email, self.signing_key, self.remotes
        )
