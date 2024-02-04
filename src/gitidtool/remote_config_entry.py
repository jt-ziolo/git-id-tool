from dataclasses import dataclass
from functools import cached_property


@dataclass
class RemoteConfigEntry:
    remote_name: str
    url: str

    @cached_property
    def hostname(self):
        return self.url.split("@", 1)[1].split(":", 1)[0]
