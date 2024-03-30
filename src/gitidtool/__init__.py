import click
import logging

from gitidtool.click_echo_wrapper import ClickEchoWrapper
from gitidtool.file_system import _read_config
from gitidtool.show_cmd_result import ShowCmdResultData, ShowCmdResultReporter

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
    help="Whether to recursively check nested repos",
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
    "-r",
    "--recursive",
    is_flag=True,
    default=False,
    show_default=True,
    help="Whether to recursively check nested repos",
)
def guard(recursive):
    git_config, gpg_config, ssh_config = _read_config(False, recursive, ".")
    results = [ShowCmdResultData(entry, gpg_config, ssh_config) for entry in git_config]

    click_echo_wrapper = ClickEchoWrapper()
    reporter = ShowCmdResultReporter()
    for result in results:
        click_echo_wrapper.echo_all()  # blank line
        reporter.report_on_result(result, click_echo_wrapper)
        click_echo_wrapper.echo_all()
        click_echo_wrapper.clear()
    pass


program.add_command(show)
program.add_command(guard)
