import click
from aws_repository.services.rds_service import start_rds_instance, stop_rds_instance

@click.group()
def rds():
    """RDS related operations"""

@rds.command()
@click.option('--db-id', required=True, help='ID of the RDS instance to stop')
def stop_instance(db_id):
    stop_rds_instance(db_id)

@rds.command()
@click.option('--db-id', required=True, help='ID of the RDS instance to start')
def start_instance(db_id):
    start_rds_instance(db_id)