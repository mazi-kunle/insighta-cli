import click
from insighta.auth import login, logout, whoami
from insighta.profiles import profiles_commands


@click.group()
def cli():
    """
    Insighta Labs CLI — Profile Intelligence Tool.
    """
    pass


# Register command groups
cli.add_command(login)
cli.add_command(logout)
cli.add_command(whoami)


cli.add_command(profiles_commands)


if __name__ == "__main__":
    cli()