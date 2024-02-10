import os
from pathlib import Path

import click

from gitidtool.click_echo_wrapper import ClickEchoWrapper
from gitidtool.git_data import GitDataEntry, GitDataEntryFactory, GitDataReader
from gitidtool.gpg_data import GpgDataEntryFactory, GpgDataReader
from gitidtool.show_cmd_result import ShowCmdResultData, ShowCmdResultReporter
from gitidtool.ssh_data import SshDataEntryFactory, SshDataReader
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
    git_config, _, _ = _read_config(
        False, False, directory, suppress_status_output
    )

    context_manager = ToolConfigJsonContextManager()
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


# Functions


def _print_id_files():
    click.echo("The following options are available (user-level ssh identity files):")


def _get_ssh_config():
    factory = SshDataEntryFactory()
    reader = SshDataReader(factory)
    return reader.get_config_entries_from_file()


def _get_gpg_config():
    factory = GpgDataEntryFactory()
    reader = GpgDataReader(factory)
    return reader.get_gpg_config()


def _get_git_config(include_global: bool, do_recursive_check: bool, relative_path: str):
    factory = GitDataEntryFactory()
    reader = GitDataReader(factory)
    config_paths = _get_git_config_paths(do_recursive_check, relative_path)
    if include_global:
        config_paths.add(Path("~/.gitconfig").expanduser())
    if len(config_paths) == 0:
        raise RuntimeError(
            f"Could not locate a git repo in the working directory ({os.getcwd()})"
        )
    result = []
    for path in config_paths:
        result.append(reader.get_git_config_from_file(path))
    return result


def _get_git_config_paths(do_recursive_check: bool, relative_path: str):
    config_paths = set[Path]()
    current_git_repo_candidate = os.path.join(
        os.getcwd(), relative_path, ".git", "config"
    )
    if Path(current_git_repo_candidate).exists():
        config_paths.add(Path(current_git_repo_candidate))
    if do_recursive_check:
        for root, directories, _ in os.walk("."):
            for directory in directories:
                if directory == ".git":
                    os_path = os.path.join(root, directory, "config")
                    config_paths.add(Path(os_path).resolve())
    return config_paths


def _read_config(
    include_global: bool,
    do_recursive_check: bool,
    relative_path: str,
    suppress_status_output: bool = False,
):
    if not suppress_status_output:
        click.echo("Reading git repo configuration files...")
    try:
        git_config: list[GitDataEntry] = _get_git_config(
            include_global, do_recursive_check, relative_path
        )
    except RuntimeError as e:
        click.echo(e)
        return
    if not suppress_status_output:
        click.echo("Reading gpg configuration...")
    gpg_config = _get_gpg_config()
    if not suppress_status_output:
        click.echo("Reading ssh configuration...")
    ssh_config = _get_ssh_config()
    return git_config, gpg_config, ssh_config
