from dataclasses import dataclass


@dataclass(frozen=True)
class GpgKeyEntry:
    public_key: str
    name: str
    email: str
