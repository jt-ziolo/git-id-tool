"""
Click echo wrapper class and related enums which provide helpful methods for
structuring and queueing command-line output.
"""

from dataclasses import dataclass, field
from enum import Enum, StrEnum

import click


class ClickEchoColor(StrEnum):
    """StrEnum representing allowed foreground text colors when echoing text to
    the command-line with click"""

    DEFAULT = "white"
    MATCH = "green"
    WARNING = "yellow"
    MISMATCH = "red"


class LineStatus(Enum):
    """Enum representing possible per-line statuses, which are used to
    determine which symbols are prepended to text."""

    DEFAULT = (0,)
    GOOD = (1,)
    WARNING = (2,)
    ERROR = (3,)


@dataclass
class ClickEchoWrapper:
    """
    Click echo wrapper class which provides helpful methods for structuring
    text decoupled from the time that the text is actually echoed to the
    command-line.
    """

    _output: list[str] = field(default_factory=list)

    def add_line(
        self,
        text: str,
        indentation_level=0,
        color: ClickEchoColor = ClickEchoColor.DEFAULT,
        isHeading=False,
        status: LineStatus = LineStatus.DEFAULT,
        insert_at_position=-1,
    ):
        """Adds a line of text to be echoed to the command-line.

        :param str text: the text to echo
        :param int indentation_level: the number of indentations preceding the
        text, defaults to 0
        :param ClickEchoColor color: the foreground color that the text should
        appear with (if ClickEchoColor.DEFAULT, will be overridden according to
        the prepended symbol), defaults to ClickEchoColor.DEFAULT
        :param bool isHeading: whether to set the text to bold, defaults to
        False
        :param LineStatus status: used to determine the symbol to prepend the
        line with (after indentation), defaults to LineStatus.DEFAULT
        :param int insert_at_position: the index to place the text at in the
        list (a value of -1 means the end of the list, emulating queueing),
        defaults to -1
        """
        indentation = ""
        for _ in range(indentation_level):
            indentation += "    "
        status_symbol = ""
        match status:
            case LineStatus.GOOD:
                color = (
                    ClickEchoColor.MATCH if color is ClickEchoColor.DEFAULT else color
                )
                status_symbol = "✅ "
            case LineStatus.WARNING:
                color = (
                    ClickEchoColor.WARNING if color is ClickEchoColor.DEFAULT else color
                )
                status_symbol = "❔ "
            case LineStatus.ERROR:
                color = (
                    ClickEchoColor.MISMATCH
                    if color is ClickEchoColor.DEFAULT
                    else color
                )
                status_symbol = "❌ "

        if insert_at_position < 0:
            self._output.append(
                click.style(
                    f"{indentation}{status_symbol}{text}", fg=color, bold=isHeading
                ),
            )
            return

        self._output.insert(
            insert_at_position,
            click.style(
                f"{indentation}{status_symbol}{text}", fg=color, bold=isHeading
            ),
        )

    def echo_all(self):
        """Echoes all lines using click. Does not clear the lines automatically."""
        click.echo("\n".join(self._output))

    def clear(self):
        """Removes all lines."""
        self._output.clear()
