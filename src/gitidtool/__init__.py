import click
import os
from pathlib import Path
from gitidtool.click_echo_color import ClickEchoColor
from gitidtool.click_echo_wrapper import ClickEchoWrapper

from gitidtool.repo_config import RepoConfig
from gitidtool.repo_config_factory import RepoConfigFactory
from gitidtool.repo_config_reader import RepoConfigReader
from gitidtool.git_config_results import GitConfigResults
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
    "-c",
    "--check-gpg",
    default=False,
    show_default=True,
    help="Checks the signing key in the git configuration file against gpg key list output and includes that information and any mismatches in the result output.",
)
def show(check_gpg):
    click.echo(f"check_gpg is {check_gpg}")
    ssh_config = _get_ssh_config()
    all_config: list[RepoConfig] = _get_git_configs()
    results, ssh_entries = _interpret_results(ssh_config, all_config)
    _report_results(all_config, results, ssh_entries)


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


def _get_git_configs():
    factory = RepoConfigFactory()
    reader = RepoConfigReader(factory)
    config_paths = _get_git_config_paths()
    result = []
    for path in config_paths:
        result.append(reader.get_git_config_from_file(path))
    return result


def _get_git_config_paths():
    config_paths: list[Path] = []
    for root, directories, _ in os.walk("."):
        for directory in directories:
            if directory == ".git":
                os_path = os.path.join(root, directory, "config")
                config_paths.append(Path(os_path).resolve())
    return config_paths


def _report_results(all_config, results, ssh_entries):
    wrapper = ClickEchoWrapper()
    for config in all_config:
        # Report per repo
        wrapper.add_line(f'For the repo located at: "{config.path}":')
        wrapper.add_line(f'- name = "{config.name}"', 1)
        text_fg = ClickEchoColor.match
        if config in results.mismatched_email_entries:
            if len(config.remotes) <= 1:
                text_fg = ClickEchoColor.mismatch
            else:
                text_fg = ClickEchoColor.potential_mismatch
        wrapper.add_line(f'- email = "{config.email}"', 1, text_fg)
        wrapper.add_line(f'- signingkey = "{config.signing_key}"', 1)
        # Report on each remote for the repo, and the associated SSH hostname
        if len(config.remotes) > 0:
            wrapper.add_line("Remotes:", 1)
        for remote in config.remotes:
            wrapper.add_line(f'- {remote.remote_name} = "{remote.url}"', 2)
            hostname = remote.hostname
            wrapper.add_line(f"hostname: {hostname}", 3)
            if hostname in results.unconfigured_hostnames:
                wrapper.add_line(
                    "(no SSH entries for that hostname)",
                    3,
                    ClickEchoColor.potential_mismatch,
                )
                continue
            ssh_entry = ssh_entries[0]
            text_fg = ClickEchoColor.match
            if (config, ssh_entry) in results.mismatched_email_entries:
                text_fg = ClickEchoColor.mismatch
            wrapper.add_line(
                f"email (SSH): {ssh_entry.email}",
                3,
                text_fg,
            )
        wrapper.add_line("") # Add a blank line between each repo's report
    if len(all_config) > 1:
        # Report on each mismatch found, if any
        has_mismatches = False
        has_mismatches = has_mismatches or len(results.names) > 1
        has_mismatches = has_mismatches or len(results.emails) > 1
        has_mismatches = has_mismatches or len(results.signing_keys) > 1
        if has_mismatches:
            wrapper.add_line("Mismatches found:", 0, ClickEchoColor.mismatch)
            wrapper.add_line(f"Names: {", ".join(results.names)}", 1)
            wrapper.add_line(f"Emails: {", ".join(results.emails)}", 1)
            wrapper.add_line(f"Signing keys: {", ".join(results.signing_keys)}", 1)
    wrapper.echo_all()


def _interpret_results(ssh_config, all_config):
    results = GitConfigResults()

    for config in all_config:
        results.names.add(f'"{config.name}"')
        results.emails.add(f'"{config.email}"')
        results.signing_keys.add(f'"{config.signing_key}"')

        for remote in config.remotes:
            hostname = remote.hostname
            ssh_entries = [entry for entry in ssh_config if entry.hostname == hostname]
            if len(ssh_entries) == 0:
                results.unconfigured_hostnames.add(hostname)
                continue
            ssh_entry = ssh_entries[0]
            if ssh_entry.email != config.email:
                results.mismatched_email_entries.append(config)
                results.mismatched_email_entries.append((config, ssh_entry))
    return results, ssh_entries
