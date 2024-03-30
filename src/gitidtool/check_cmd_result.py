from functools import cached_property

from gitidtool.click_echo_wrapper import ClickEchoWrapper, LineStatus
from gitidtool.git_data import GitDataEntry, GitRemoteDataEntry
from gitidtool.gpg_data import GpgDataEntry
from gitidtool.ssh_data import SshDataEntry


class CheckCmdResultData:
    def __init__(
        self,
        repo_config_entry: GitDataEntry,
        gpg_config: list[GpgDataEntry],
        ssh_config: list[SshDataEntry],
    ):
        self.gpg_config_entry = repo_config_entry.get_gpg_entry_matching_signing_key(
            gpg_config
        )
        self.ssh_map = dict[GitRemoteDataEntry, SshDataEntry]()
        for remote in repo_config_entry.remotes:
            self.ssh_map[remote] = remote.get_ssh_entry_matching_hostname(ssh_config)
        self.remotes = repo_config_entry.remotes
        self.repo_config_entry = repo_config_entry

    @cached_property
    def git_repo_path(self):
        return self.repo_config_entry.path

    @cached_property
    def git_repo_folder_name(self):
        return (
            "GLOBAL"
            if str(self.repo_config_entry.path).endswith(".gitconfig")
            else self.repo_config_entry.repo_folder_name
        )

    @cached_property
    def git_user_name(self):
        return self.repo_config_entry.name

    @cached_property
    def git_user_email(self):
        return self.repo_config_entry.email

    @cached_property
    def git_user_signing_key(self):
        return self.repo_config_entry.signing_key

    @cached_property
    def gpg_uid_name(self):
        return self.gpg_config_entry.name

    @cached_property
    def gpg_uid_email(self):
        return self.gpg_config_entry.email
    
    @cached_property
    def is_consistent(self):
        return False

    def get_ssh_entry_for_remote(self, remote: GitRemoteDataEntry):
        return self.ssh_map[remote]


class CheckCmdResultReporter:
    def report_on_result(
        self, git_result: CheckCmdResultData, click_echo_wrapper: ClickEchoWrapper
    ):
        worst_status = LineStatus.GOOD

        indentation_level = 0
        indentation_level += 1
        click_echo_wrapper.add_line(
            f'git: user.name = "{git_result.git_user_name}"',
            indentation_level,
        )
        if git_result.git_user_name == "":
            click_echo_wrapper.add_line(
                "Missing git user name",
                indentation_level + 1,
                status=LineStatus.WARNING,
            )
            worst_status = LineStatus.WARNING
        click_echo_wrapper.add_line(
            f'git: user.email = "{git_result.git_user_email}"',
            indentation_level,
        )
        if git_result.git_user_name == "":
            click_echo_wrapper.add_line(
                "Missing git user email",
                indentation_level + 1,
                status=LineStatus.WARNING,
            )
            worst_status = LineStatus.WARNING
        click_echo_wrapper.add_line(
            f'git: user.signingkey = "{git_result.git_user_signing_key}"',
            indentation_level,
        )
        indentation_level += 1
        if git_result.git_user_signing_key == "":
            click_echo_wrapper.add_line(
                "No signing key set for this repo",
                indentation_level,
                status=LineStatus.WARNING,
            )
            worst_status = LineStatus.WARNING
        else:
            worst_status = self.add_line_check_mismatch(
                worst_status,
                click_echo_wrapper,
                indentation_level,
                f"gpg ({git_result.git_user_signing_key}): uid.name",
                git_result.gpg_uid_name,
                "git user.name",
                git_result.git_user_name,
            )
            worst_status = self.add_line_check_mismatch(
                worst_status,
                click_echo_wrapper,
                indentation_level,
                f"gpg ({git_result.git_user_signing_key}): uid.email",
                git_result.gpg_uid_email,
                "git user.email",
                git_result.git_user_email,
            )
        indentation_level -= 1
        if len(git_result.remotes) == 0:
            if git_result.git_repo_folder_name != "GLOBAL":
                click_echo_wrapper.add_line(
                    "No remotes configured for this repo",
                    indentation_level,
                    status=LineStatus.WARNING 
                )
                worst_status = (
                    LineStatus.WARNING if worst_status == LineStatus.GOOD else worst_status
                )
        for remote in git_result.remotes:
            click_echo_wrapper.add_line(
                f'git: [remote "{remote.remote_name}"].url = "{remote.url}"',
                indentation_level,
            )
            ssh_entry = git_result.get_ssh_entry_for_remote(remote)
            if ssh_entry is None:
                click_echo_wrapper.add_line(
                    "No known ssh host with this hostname",
                    indentation_level + 1,
                    status=LineStatus.WARNING,
                )
                worst_status = LineStatus.WARNING
            else:
                indentation_level += 1
                click_echo_wrapper.add_line(
                    f'ssh (Host: "{ssh_entry.hostname}" => IdentityFile: "{ssh_entry.identity_file_path}")',
                    indentation_level,
                )
                worst_status = self.add_line_check_mismatch(
                    worst_status,
                    click_echo_wrapper,
                    indentation_level,
                    "=> email",
                    ssh_entry.email,
                    "git user.email",
                    git_result.git_user_email,
                )
        click_echo_wrapper.add_line(
            f"{git_result.git_repo_folder_name} ({git_result.git_repo_path})",
            0,
            isHeading=True,
            status=worst_status,
            insert_at_position=0,
        )

    def add_line_check_mismatch(
        self,
        worst_status,
        click_echo_wrapper: ClickEchoWrapper,
        indentation_level,
        desc,
        value,
        desc_checking_against: str,
        value_checking_against,
    ):
        click_echo_wrapper.add_line(
            f'{desc} = "{value}"',
            indentation_level,
        )
        if value == value_checking_against:
            click_echo_wrapper.add_line(
                f"Matches {desc_checking_against}",
                indentation_level + 1,
                status=LineStatus.GOOD,
            )
            return worst_status  # no worse than it was entering this call
        if value != value_checking_against:
            click_echo_wrapper.add_line(
                f"Does not match {desc_checking_against}",
                indentation_level + 1,
                status=LineStatus.ERROR,
            )
            return LineStatus.ERROR
