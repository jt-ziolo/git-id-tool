from dataclasses import dataclass, field
import click
from gitidtool.click_echo_color import ClickEchoColor


@dataclass
class ClickEchoWrapper:
    output: list[str] = field(default_factory=list)

    def add_line(
        self, text, indentation_level=0, color: ClickEchoColor = ClickEchoColor.default
    ):
        indentation = ""
        for _ in range(indentation_level):
            indentation += "  "
        self.output.append(click.style(f"{indentation}{text}", fg=color))

    def echo_all(self):
        click.echo("\n".join(self.output))

    def clear(self):
        self.output.clear()
