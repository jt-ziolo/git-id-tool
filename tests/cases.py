from dataclasses import dataclass, field
import random
from faker import Faker

from gitidtool.git_data import GitDataEntry, GitRemoteDataEntry
from gitidtool.gpg_data import GpgDataEntry
from gitidtool.ssh_data import SshDataEntry


@dataclass
class Case:
    git_data: list[GitDataEntry] = field(default_factory=list)
    gpg_data: list[GpgDataEntry] = field(default_factory=list)
    ssh_data: list[SshDataEntry] = field(default_factory=list)

    def __repr__(self):
        return f"[git_data={repr(self.git_data)}, gpg_data={repr(self.gpg_data)}, ssh_data={repr(self.ssh_data)}]"


def generate_signing_key(seed: str = ""):
    # signing_key: 16 random uppercase alphanumeric chars
    if seed != "":
        random.seed(seed)
    signing_key = ""
    for _ in range(16):
        signing_key += random.choice(
            [char for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"]
        )
    return signing_key


def generate_signing_key_from_details(user_name, email):
    return generate_signing_key(f"{user_name}{email}")


def generate_signing_key_faker(faker):
    return generate_signing_key(faker.word())


@dataclass
class GitRemoteDataEntryGenerator:
    remote_name: str = ""
    hostname: str = ""

    def generate(self, faker: Faker):
        remote_name = self.remote_name if self.remote_name != "" else faker.word()
        hostname = self.hostname if self.hostname != "" else f"{faker.word()}.com"
        return GitRemoteDataEntry(
            remote_name, f"git@{hostname}:user-name/repo-name.git"
        )


@dataclass
class GitDataEntryGenerator:
    hostname: str = ""
    email: str = ""
    hostname: str = ""
    user_name: str = ""
    remotes: list[GitRemoteDataEntry] = field(default_factory=list)
    repo_name: str = ""
    signing_key: str = ""

    def generate(self, faker: Faker):
        repo_name = (
            self.repo_name if self.repo_name != "" else f"{faker.word()}{faker.word()}"
        )
        user_name = self.user_name if self.user_name != "" else faker.name()
        email = self.email if self.email != "" else faker.email()
        signing_key = (
            self.signing_key
            if self.signing_key != ""
            else generate_signing_key_faker(faker)
        )
        remotes = self.remotes if self.remotes else []
        if len(remotes) == 0:
            # Generate 1 to 3 with the hostname
            generator = GitRemoteDataEntryGenerator(hostname=self.hostname)
            for _ in range(random.randrange(1, 3)):
                remotes.append(generator.generate(faker))
        return GitDataEntry(
            f"{repo_name}/.git/config", user_name, email, signing_key, remotes
        )


@dataclass
class GpgDataEntryGenerator:
    email: str = ""
    user_name: str = ""
    signing_key: str = ""

    def generate(self, faker: Faker):
        user_name = self.user_name if self.user_name != "" else faker.name()
        email = self.email if self.email != "" else faker.email()
        signing_key = (
            self.signing_key
            if self.signing_key != ""
            else generate_signing_key_faker(faker)
        )
        return GpgDataEntry(signing_key, user_name, email)


@dataclass
class SshDataEntryGenerator:
    email: str = ""
    hostname: str = ""

    def generate(self, faker: Faker):
        email = self.email if self.email != "" else faker.email()
        hostname = self.hostname if self.hostname != "" else f"{faker.word()}.com"
        return SshDataEntry(hostname, email, f"~/.ssh/id-file-{random.randrange(1000)}")


@dataclass
class CaseGenerator:
    faker: Faker

    email: str = ""
    hostname: str = ""
    user_name: str = ""
    remotes: list[GitRemoteDataEntry] = field(default_factory=list)
    repo_name: str = ""
    signing_key: str = ""

    git_data_generator: GitDataEntryGenerator = None
    gpg_data_generator: GpgDataEntryGenerator = None
    ssh_data_generator: SshDataEntryGenerator = None

    def generate_git(
        self, combine_with: Case = None, override_from_output: bool = False
    ):
        self.git_data_generator = (
            self.git_data_generator
            if self.git_data_generator
            else GitDataEntryGenerator(
                self.hostname,
                self.email,
                self.user_name,
                self.remotes,
                self.repo_name,
                self.signing_key,
            )
        )
        entry = self.git_data_generator.generate(self.faker)
        if override_from_output:
            self.email = entry.email
            self.user_name = entry.name
            self.remotes = entry.remotes
            self.signing_key = entry.signing_key
        if combine_with:
            temp_data = combine_with.git_data.copy()
            temp_data.append(entry)
            return Case(
                temp_data, combine_with.gpg_data.copy(), combine_with.ssh_data.copy()
            )
        return Case(git_data=[entry])

    def generate_gpg(
        self, combine_with: Case = None, override_from_output: bool = False
    ):
        self.gpg_data_generator = (
            self.gpg_data_generator
            if self.gpg_data_generator
            else GpgDataEntryGenerator(
                self.email,
                self.user_name,
                self.signing_key,
            )
        )
        entry = self.gpg_data_generator.generate(self.faker)
        if override_from_output:
            self.email = entry.email
            self.user_name = entry.name
            self.signing_key = entry.public_key
        if combine_with:
            temp_data = combine_with.gpg_data.copy()
            temp_data.append(entry)
            return Case(
                combine_with.git_data.copy(), temp_data, combine_with.ssh_data.copy()
            )
        return Case(gpg_data=[entry])

    def generate_ssh(
        self, combine_with: Case = None, override_from_output: bool = False
    ):
        self.ssh_data_generator = (
            self.ssh_data_generator
            if self.ssh_data_generator
            else SshDataEntryGenerator(
                self.email,
                self.hostname,
            )
        )
        entry = self.ssh_data_generator.generate(self.faker)
        if override_from_output:
            self.email = entry.email
            self.hostname = entry.hostname
        if combine_with:
            temp_data = combine_with.ssh_data.copy()
            temp_data.append(entry)
            return Case(
                combine_with.git_data.copy(), combine_with.gpg_data.copy(), temp_data
            )
        return Case(ssh_data=[entry])
