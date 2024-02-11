import click
import logging

from gitidtool.click_echo_wrapper import ClickEchoWrapper
from gitidtool.file_system import _read_config
from gitidtool.show_cmd_result import ShowCmdResultData, ShowCmdResultReporter
from gitidtool.tool_config import ToolConfigEntryFactory, ToolConfigJsonContextManager

# Click functions (API)


@click.group()
def program():
    # common functionality across grouped commands
    # click.echo(f"Nothing to do.")
    pass


@click.command()
@click.option(
    "-g",
    "--global",
    "global_",
    is_flag=True,
    default=False,
    show_default=True,
    help="Whether to include global .gitconfig results",
)
@click.option(
    "-r",
    "--recursive",
    is_flag=True,
    default=False,
    show_default=True,
    help="Whether to recursively report on all git repos including those located in subdirectories",
)
def show(global_, recursive):
    git_config, gpg_config, ssh_config = _read_config(global_, recursive, ".")
    results = [ShowCmdResultData(entry, gpg_config, ssh_config) for entry in git_config]

    click_echo_wrapper = ClickEchoWrapper()
    reporter = ShowCmdResultReporter()
    for result in results:
        click_echo_wrapper.echo_all()  # blank line
        reporter.report_on_result(result, click_echo_wrapper)
        click_echo_wrapper.echo_all()
        click_echo_wrapper.clear()


@click.command()
@click.option(
    "-d",
    "--directory",
    type=click.Path(exists=True),
    default=".",
    show_default=True,
    help="The git directory to reference",
)
@click.option(
    "--suppress-status-output",
    is_flag=True,
    default=True,
    show_default=True,
    help="Whether to suppress non-json output",
)
def write(directory, suppress_status_output):
    git_config, _, _ = _read_config(False, False, directory, suppress_status_output)

    context_manager = ToolConfigJsonContextManager(logging.root)
    factory = ToolConfigEntryFactory()
    with context_manager as config:
        for entry in git_config:
            config.add(factory.create_from_git_data_entry(entry))


@click.command()
@click.option(
    "-d",
    "--directory",
    type=click.Path(exists=True),
    default=".",
    show_default=True,
    help="The git directory to apply the configuration to",
)
@click.option(
    "-r",
    "--recursive",
    is_flag=True,
    default=False,
    show_default=True,
    help="Whether to recursively report on all git repos including those located in subdirectories",
)
@click.argument("json-input-or-path")
def use(directory, recursive, json_input_or_path):
    pass


program.add_command(show)
program.add_command(write)
program.add_command(use)