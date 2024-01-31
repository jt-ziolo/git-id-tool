import click


def get_ids():
    return "example, exampleB, hello"


@click.group()
def program():
    # common functionality across grouped commands
    click.echo(f"ABC")
    pass


@click.command()
def current():
    click.echo(get_ids())


@click.command()
def which():
    current()


@click.command()
@click.option("--count", default=1, help="Number of greetings.")
def example(count):
    for x in range(count):
        click.echo(f"Hello world!")


program.add_command(current)
program.add_command(which)
program.add_command(example)
