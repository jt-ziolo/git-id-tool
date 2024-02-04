import click
import os
from pathlib import Path
from gitidtool.click_echo_wrapper import ClickEchoWrapper
from gitidtool.git_result import GitResultData
from gitidtool.git_result_reporter import GitResultReporter
from gitidtool.gpg_key_entry_factory import GpgKeyEntryFactory
from gitidtool.gpg_key_entry_reader import GpgKeyEntryReader
from gitidtool.repo_config import RepoConfig
from gitidtool.repo_config_factory import RepoConfigFactory
from gitidtool.repo_config_reader import RepoConfigReader
from gitidtool.ssh_config_entry_factory import SshConfigEntryFactory
from gitidtool.ssh_config_reader import SshConfigReader

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
    click.echo("Reading git repo configuration files...")
    try:
        git_config: list[RepoConfig] = _get_git_config(global_, recursive)
    except RuntimeError as e:
        click.echo(e)
        return
    click.echo("Reading gpg configuration...")
    gpg_config = _get_gpg_config()
    click.echo("Reading ssh configuration...")
    ssh_config = _get_ssh_config()
    results = [GitResultData(entry, gpg_config, ssh_config) for entry in git_config]

    click_echo_wrapper = ClickEchoWrapper()
    reporter = GitResultReporter()
    for result in results:
        click_echo_wrapper.echo_all()  # blank line
        reporter.report_on_result(result, click_echo_wrapper)
        click_echo_wrapper.echo_all()
        click_echo_wrapper.clear()


@click.command()
@click.argument("git-dir", type=click.Path(exists=True))
def copy(git_dir):
    click.echo(f"git_dir is {git_dir}")


@click.command()
def make_global():
    click.echo("make_global")


@click.command()
@click.argument("id-file", required=False)
def use(id_file):
    click.echo(f"id_file is {id_file}")
    if id_file is None:
        _print_id_files()


program.add_command(show)
program.add_command(copy)
program.add_command(make_global)
program.add_command(use)


# Functions


def _print_id_files():
    click.echo("The following options are available (user-level ssh identity files):")


def _get_ssh_config():
    factory = SshConfigEntryFactory()
    reader = SshConfigReader(factory)
    return reader.get_config_entries_from_file()


def _get_gpg_config():
    factory = GpgKeyEntryFactory()
    reader = GpgKeyEntryReader(factory)
    return reader.get_gpg_config()


def _get_git_config(include_global: bool, do_recursive_check: bool):
    factory = RepoConfigFactory()
    reader = RepoConfigReader(factory)
    config_paths = _get_git_config_paths(do_recursive_check)
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


def _get_git_config_paths(do_recursive_check: bool):
    config_paths = set[Path]()
    current_git_repo_candidate = os.path.join(os.getcwd(), ".git", "config")
    if Path(current_git_repo_candidate).exists():
        config_paths.add(Path(current_git_repo_candidate))
    if do_recursive_check:
        for root, directories, _ in os.walk("."):
            for directory in directories:
                if directory == ".git":
                    os_path = os.path.join(root, directory, "config")
                    config_paths.add(Path(os_path).resolve())
    return config_paths
