from dataclasses import dataclass, field
from enum import Enum
import click
from gitidtool.click_echo_color import ClickEchoColor


class StatusSymbol(Enum):
    NONE = (0,)
    CHECK = (1,)
    QUESTION_MARK = (2,)
    CROSS_OUT = (3,)


@dataclass
class ClickEchoWrapper:
    output: list[str] = field(default_factory=list)

    def add_line(
        self,
        text,
        indentation_level=0,
        color: ClickEchoColor = ClickEchoColor.DEFAULT,
        isHeading=False,
        prependedSymbol: StatusSymbol = StatusSymbol.NONE,
        insert_at_position=-1,
    ):
        indentation = ""
        for _ in range(indentation_level):
            indentation += "    "
        status_symbol = ""
        match prependedSymbol:
            case StatusSymbol.CHECK:
                status_symbol = "✅ "
            case StatusSymbol.QUESTION_MARK:
                status_symbol = "❔ "
            case StatusSymbol.CROSS_OUT:
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
        prependedSymbol: StatusSymbol = StatusSymbol.NONE,
        insert_at_position=-1,
    ):
        indentation = ""
        for _ in range(indentation_level):
            indentation += "    "
        status_symbol = ""
        match prependedSymbol:
            case StatusSymbol.CHECK:
                color = ClickEchoColor.MATCH
                status_symbol = "✅ "
            case StatusSymbol.QUESTION_MARK:
                color = ClickEchoColor.WARNING
                status_symbol = "❔ "
            case StatusSymbol.CROSS_OUT:
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
