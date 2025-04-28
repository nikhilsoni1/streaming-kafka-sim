import click
from .cli_commands import ec2
from .cli_commands import s3
from .cli_commands import rds


@click.group()
def cli():
    """Skyhawk: Lightweight Tactical AWS CLI"""


cli.add_command(ec2)
cli.add_command(s3)
cli.add_command(rds)

if __name__ == "__main__":
    cli()
