import click
from aws_repository.services.security_service import list_security_rules


@click.group()
def security():
    """Security Group related operations"""


@security.command()
def list_rules():
    rules = list_security_rules()
    click.echo(rules)
