from gitidtool.click_echo_wrapper import ClickEchoWrapper, StatusSymbol
from gitidtool.git_result import GitResultData


class GitResultReporter:
    def report_on_result(
        self, git_result: GitResultData, click_echo_wrapper: ClickEchoWrapper
    ):
        worst_status = StatusSymbol.CHECK

        indentation_level = 0
        indentation_level += 1
        click_echo_wrapper.add_line(
            f'git: user.name = "{git_result.git_user_name}"',
            indentation_level,
        )
        if git_result.git_user_name == "":
            click_echo_wrapper.add_status_line(
                "Missing git user name",
                indentation_level + 1,
                prependedSymbol=StatusSymbol.QUESTION_MARK,
            )
            worst_status = StatusSymbol.QUESTION_MARK
        click_echo_wrapper.add_line(
            f'git: user.email = "{git_result.git_user_email}"',
            indentation_level,
        )
        if git_result.git_user_name == "":
            click_echo_wrapper.add_status_line(
                "Missing git user email",
                indentation_level + 1,
                prependedSymbol=StatusSymbol.QUESTION_MARK,
            )
            worst_status = StatusSymbol.QUESTION_MARK
        click_echo_wrapper.add_line(
            f'git: user.signingkey = "{git_result.git_user_signing_key}"',
            indentation_level,
        )
        indentation_level += 1
        if git_result.git_user_signing_key == "":
            click_echo_wrapper.add_status_line(
                "No signing key set for this repo",
                indentation_level,
                prependedSymbol=StatusSymbol.QUESTION_MARK,
            )
            worst_status = StatusSymbol.QUESTION_MARK
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
            click_echo_wrapper.add_status_line(
                f"No remotes configured for this repo",
                indentation_level,
                prependedSymbol=StatusSymbol.QUESTION_MARK,
            )
            worst_status = (
                StatusSymbol.QUESTION_MARK
                if worst_status == StatusSymbol.CHECK
                else worst_status
            )
        for remote in git_result.remotes:
            click_echo_wrapper.add_line(
                f'git: [remote "{remote.remote_name}"].url = "{remote.url}"',
                indentation_level,
            )
            # click_echo_wrapper.add_line(
            #     f'=> hostname = "{remote.hostname}"',
            #     indentation_level,
            # )
            ssh_entry = git_result.get_ssh_entry_for_remote(remote)
            if ssh_entry is None:
                click_echo_wrapper.add_status_line(
                    f"No known ssh host with this hostname",
                    indentation_level + 1,
                    prependedSymbol=StatusSymbol.QUESTION_MARK,
                )
                worst_status = StatusSymbol.QUESTION_MARK
            else:
                indentation_level += 1
                click_echo_wrapper.add_line(
                    f'ssh (Host: "{ssh_entry.hostname}" => IdentityFile: "{ssh_entry.identity_file_path}")',
                    indentation_level,
                )
                # click_echo_wrapper.add_line(
                #     f'email = "{ssh_entry.email}"',
                #     indentation_level,
                # )
                worst_status = self.add_line_check_mismatch(
                    worst_status,
                    click_echo_wrapper,
                    indentation_level,
                    "=> email",
                    ssh_entry.email,
                    "git user.email",
                    git_result.git_user_email,
                )
                # indentation_level -= 1
        click_echo_wrapper.add_status_line(
            f"{git_result.git_repo_folder_name} ({git_result.git_repo_path})",
            0,
            True,
            worst_status,
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
            click_echo_wrapper.add_status_line(
                f"Matches {desc_checking_against}",
                indentation_level + 1,
                prependedSymbol=StatusSymbol.CHECK,
            )
            return worst_status  # no worse than it was entering this call
        if value != value_checking_against:
            click_echo_wrapper.add_status_line(
                f"Does not match {desc_checking_against}",
                indentation_level + 1,
                prependedSymbol=StatusSymbol.CROSS_OUT,
            )
            return StatusSymbol.CROSS_OUT
