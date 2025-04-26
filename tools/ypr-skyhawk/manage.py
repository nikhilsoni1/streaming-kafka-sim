import click
from commands import ec2
from commands import s3
from commands import rds
from commands import emr
from commands import security


@click.group()
def cli():
    """Skyhawk: Lightweight Tactical AWS CLI"""

cli.add_command(ec2)
cli.add_command(s3)
cli.add_command(rds)
cli.add_command(emr)
cli.add_command(security)

if __name__ == "__main__":
    cli()