import click

from gitidtool.click_echo_wrapper import ClickEchoWrapper
from gitidtool.file_system import _read_config
from gitidtool.check_cmd_result import CheckCmdResultData, CheckCmdResultReporter

# Click functions (API)


@click.group()
def program():
    # common functionality across grouped commands
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
def check(global_, recursive):
    git_config, gpg_config, ssh_config = _read_config(global_, recursive, ".")
    results = [CheckCmdResultData(entry, gpg_config, ssh_config) for entry in git_config]

    click_echo_wrapper = ClickEchoWrapper()
    reporter = CheckCmdResultReporter()
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
    results = [CheckCmdResultData(entry, gpg_config, ssh_config) for entry in git_config]


program.add_command(check)
program.add_command(guard)
