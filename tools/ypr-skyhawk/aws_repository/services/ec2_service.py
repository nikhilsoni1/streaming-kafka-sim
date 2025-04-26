import time
import click
from aws_repository.services.common_service import create_boto3_client

def poll_instance_status(ec2_client, instance_id: str, desired_state: str, wait_interval: int = 5, timeout: int = 300):
    """
    Polls the EC2 instance status until it reaches the desired state, or timeout occurs.

    Args:
        ec2_client (boto3.client): EC2 boto3 client.
        instance_id (str): The ID of the EC2 instance.
        desired_state (str): Target state ('running', 'stopped').
        wait_interval (int): Seconds between status checks.
        timeout (int): Maximum seconds to wait before giving up.
    """
    start_time = time.time()

    click.echo(f"Waiting for instance {instance_id} to reach state '{desired_state}' (timeout {timeout}s)...")

    with click.progressbar(length=timeout, label='Polling EC2 instance status') as bar:
        while True:
            response = ec2_client.describe_instances(InstanceIds=[instance_id])
            state = response['Reservations'][0]['Instances'][0]['State']['Name']
            elapsed_time = time.time() - start_time

            if state == desired_state:
                click.echo(f"\nInstance {instance_id} is now '{desired_state}'.")
                break

            if elapsed_time > timeout:
                raise TimeoutError(f"\nTimeout waiting for instance {instance_id} to reach '{desired_state}'. "
                                   f"Last known state: {state}")

            time.sleep(wait_interval)
            bar.update(wait_interval)

def ec2_stop_instance(instance_id: str, region: str = "us-east-1", wait: bool = False):
    """
    Stop an EC2 instance and optionally wait until it is fully stopped.
    """
    ec2 = create_boto3_client('ec2', region)
    ec2.stop_instances(InstanceIds=[instance_id])

    if wait:
        poll_instance_status(ec2, instance_id, desired_state='stopped')

def ec2_start_instance(instance_id: str, region: str = "us-east-1", wait: bool = False):
    """
    Start an EC2 instance and optionally wait until it is fully running.
    """
    ec2 = create_boto3_client('ec2', region)
    ec2.start_instances(InstanceIds=[instance_id])

    if wait:
        poll_instance_status(ec2, instance_id, desired_state='running')

def ec2_update_instance_ip(instance_id: str, new_ip: str, region: str = "us-east-1"):
    """
    Update EC2 instance public IP address.
    """
    ec2 = create_boto3_client('ec2', region)
    ec2.modify_instance_attribute(InstanceId=instance_id, SourceDestCheck={'Value': False})

def paginate_describe_instances(ec2_client) -> list:
    """
    Paginate through all EC2 instances in the region.

    Args:
        ec2_client (boto3.client): EC2 boto3 client.

    Returns:
        list: A list of EC2 instance dictionaries.
    """
    instances = []
    paginator = ec2_client.get_paginator('describe_instances')

    for page in paginator.paginate():
        for reservation in page.get('Reservations', []):
            for instance in reservation.get('Instances', []):
                instances.append({
                    'InstanceId': instance.get('InstanceId'),
                    'State': instance.get('State', {}).get('Name'),
                    'InstanceType': instance.get('InstanceType'),
                    'PublicIpAddress': instance.get('PublicIpAddress'),
                    'PrivateIpAddress': instance.get('PrivateIpAddress'),
                    'LaunchTime': str(instance.get('LaunchTime'))
                })
    return instances

def ec2_list_all_instances(region: str = "us-east-1") -> list:
    """
    List all EC2 instances in the specified AWS region.
    """
    ec2 = create_boto3_client('ec2', region)
    return paginate_describe_instances(ec2)
