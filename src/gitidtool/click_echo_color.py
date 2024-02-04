from dataclasses import dataclass


@dataclass(frozen=True)
class ClickEchoColor:
    match = "green"
    potential_mismatch = "yellow"
    mismatch = "red"
    default = "white"
