import click

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
        print_id_files()


program.add_command(show)
program.add_command(copy)
program.add_command(use)


# Functions


def print_id_files():
    click.echo(f"The following options are available (user-level ssh identity files):")
