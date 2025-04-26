import time
import click
from aws_repository.services.common_service import create_boto3_client

def poll_rds_instance_status(rds_client, db_instance_id: str, desired_status: str, wait_interval: int = 10, timeout: int = 600):
    """
    Polls the RDS DB instance status until it reaches the desired status, or timeout occurs.

    Args:
        rds_client (boto3.client): RDS boto3 client.
        db_instance_id (str): The DB instance identifier.
        desired_status (str): Target status ('available', 'stopped').
        wait_interval (int): Seconds between status checks.
        timeout (int): Maximum seconds to wait before giving up.
    """
    start_time = time.time()

    click.echo(f"Waiting for RDS instance {db_instance_id} to reach status '{desired_status}' (timeout {timeout}s)...")

    with click.progressbar(length=timeout, label='Polling RDS instance status') as bar:
        while True:
            response = rds_client.describe_db_instances(DBInstanceIdentifier=db_instance_id)
            current_status = response['DBInstances'][0]['DBInstanceStatus']
            elapsed_time = time.time() - start_time

            if current_status == desired_status:
                click.echo(f"\nRDS instance {db_instance_id} is now '{desired_status}'.")
                break

            if elapsed_time > timeout:
                raise TimeoutError(f"\nTimeout waiting for RDS instance {db_instance_id} to reach '{desired_status}'. "
                                   f"Last known status: {current_status}")

            time.sleep(wait_interval)
            bar.update(wait_interval)

def rds_start_instance(db_id: str, region: str = "us-east-1", wait: bool = False):
    """
    Start an RDS DB instance and optionally wait until it is available.
    """
    rds = create_boto3_client('rds', region)
    rds.start_db_instance(DBInstanceIdentifier=db_id)

    if wait:
        poll_rds_instance_status(rds, db_id, desired_status='available')

def rds_stop_instance(db_id: str, region: str = "us-east-1", wait: bool = False):
    """
    Stop an RDS DB instance and optionally wait until it is stopped.
    """
    rds = create_boto3_client('rds', region)
    rds.stop_db_instance(DBInstanceIdentifier=db_id)

    if wait:
        poll_rds_instance_status(rds, db_id, desired_status='stopped')

def paginate_describe_db_instances(rds_client) -> list:
    """
    Paginate through all RDS DB instances in the region.

    Args:
        rds_client (boto3.client): RDS boto3 client.

    Returns:
        list: A list of RDS instance dictionaries.
    """
    instances = []
    paginator = rds_client.get_paginator('describe_db_instances')

    for page in paginator.paginate():
        for db_instance in page.get('DBInstances', []):
            instances.append({
                'DBInstanceIdentifier': db_instance.get('DBInstanceIdentifier'),
                'DBInstanceStatus': db_instance.get('DBInstanceStatus'),
                'Engine': db_instance.get('Engine'),
                'DBInstanceClass': db_instance.get('DBInstanceClass'),
                'Endpoint': db_instance.get('Endpoint', {}).get('Address'),
                'AllocatedStorage': db_instance.get('AllocatedStorage'),
                'InstanceCreateTime': str(db_instance.get('InstanceCreateTime'))
            })
    return instances

def rds_list_all_instances(region: str = "us-east-1") -> list:
    """
    List all RDS DB instances in the specified AWS region.
    """
    rds = create_boto3_client('rds', region)
    return paginate_describe_db_instances(rds)
