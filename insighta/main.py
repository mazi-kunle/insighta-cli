import click
from insighta.auth import auth_commands
from insighta.profiles import profiles_commands


@click.group()
def cli():
    """
    Insighta Labs CLI — Profile Intelligence Tool.
    """
    pass


# Register command groups
cli.add_command(auth_commands)
cli.add_command(profiles_commands)


if __name__ == "__main__":
    cli()