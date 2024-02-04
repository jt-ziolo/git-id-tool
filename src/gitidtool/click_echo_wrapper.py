from dataclasses import dataclass, field
from enum import Enum, StrEnum

import click


class ClickEchoColor(StrEnum):
    DEFAULT = "white"
    MATCH = "green"
    WARNING = "yellow"
    MISMATCH = "red"


class LineStatus(Enum):
    DEFAULT = (0,)
    GOOD = (1,)
    WARNING = (2,)
    ERROR = (3,)


@dataclass
class ClickEchoWrapper:
    output: list[str] = field(default_factory=list)

    def add_line(
        self,
        text,
        indentation_level=0,
        color: ClickEchoColor = ClickEchoColor.DEFAULT,
        isHeading=False,
        prependedSymbol: LineStatus = LineStatus.DEFAULT,
        insert_at_position=-1,
    ):
        indentation = ""
        for _ in range(indentation_level):
            indentation += "    "
        status_symbol = ""
        match prependedSymbol:
            case LineStatus.GOOD:
                status_symbol = "✅ "
            case LineStatus.WARNING:
                status_symbol = "❔ "
            case LineStatus.ERROR:
                status_symbol = "❌ "

        if insert_at_position < 0:
            self.output.append(
                click.style(
                    f"{indentation}{status_symbol}{text}", fg=color, bold=isHeading
                ),
            )
            return

        self.output.insert(
            insert_at_position,
            click.style(
                f"{indentation}{status_symbol}{text}", fg=color, bold=isHeading
            ),
        )

    def add_status_line(
        self,
        text,
        indentation_level=0,
        isHeading=False,
        prependedSymbol: LineStatus = LineStatus.DEFAULT,
        insert_at_position=-1,
    ):
        indentation = ""
        for _ in range(indentation_level):
            indentation += "    "
        status_symbol = ""
        match prependedSymbol:
            case LineStatus.GOOD:
                color = ClickEchoColor.MATCH
                status_symbol = "✅ "
            case LineStatus.WARNING:
                color = ClickEchoColor.WARNING
                status_symbol = "❔ "
            case LineStatus.ERROR:
                color = ClickEchoColor.MISMATCH
                status_symbol = "❌ "

        if insert_at_position < 0:
            self.output.append(
                click.style(
                    f"{indentation}{status_symbol}{text}", fg=color, bold=isHeading
                ),
            )
            return

        self.output.insert(
            insert_at_position,
            click.style(
                f"{indentation}{status_symbol}{text}", fg=color, bold=isHeading
            ),
        )

    def echo_all(self):
        click.echo("\n".join(self.output))

    def clear(self):
        self.output.clear()
