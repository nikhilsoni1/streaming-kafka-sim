import click
from commands import ec2
from commands import s3
from commands.rds_commands import rds
from commands.emr_commands import emr
from commands.security_commands import security


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