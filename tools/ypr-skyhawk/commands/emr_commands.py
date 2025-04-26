import click
from aws_repository.services.emr_service import list_emr_configurations

@click.group()
def emr():
    """EMR related operations"""

@emr.command()
def list_configs():
    configs = list_emr_configurations()
    click.echo(configs)