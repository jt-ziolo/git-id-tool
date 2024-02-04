from functools import cached_property
from gitidtool.gpg_key_entry import GpgKeyEntry
from gitidtool.remote_config_entry import RemoteConfigEntry
from gitidtool.repo_config import RepoConfig
from gitidtool.ssh_config_entry import SshConfigEntry


class GitResultData:
    def __init__(
        self,
        repo_config_entry: RepoConfig,
        gpg_config: list[GpgKeyEntry],
        ssh_config: list[SshConfigEntry],
    ):
        self.gpg_config_entry = repo_config_entry.get_gpg_entry_matching_signing_key(
            gpg_config
        )
        self.ssh_map = dict[RemoteConfigEntry, SshConfigEntry]()
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

    def get_ssh_entry_for_remote(self, remote: RemoteConfigEntry):
        return self.ssh_map[remote]
