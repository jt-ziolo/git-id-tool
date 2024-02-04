from gitidtool.remote_config_entry import RemoteConfigEntry
from dataclasses import dataclass, field


@dataclass
class RepoConfig:
    path: str = ""
    name: str = ""
    email: str = ""
    signing_key: str = ""
    remotes: list[RemoteConfigEntry] = field(default_factory=list)
