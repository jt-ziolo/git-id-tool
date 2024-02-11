import os
from pathlib import Path

import click
from gitidtool.git_data import GitDataEntry, GitDataEntryFactory, GitDataReader
from gitidtool.gpg_data import GpgDataEntryFactory, GpgDataReader
from gitidtool.ssh_data import SshDataEntryFactory, SshDataReader


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
