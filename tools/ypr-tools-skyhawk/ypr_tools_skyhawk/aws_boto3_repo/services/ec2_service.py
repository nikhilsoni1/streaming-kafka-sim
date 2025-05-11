import time
import click
from .common_service import create_boto3_client
from yaspin import yaspin
import ipaddress
import pandas as pd
from itertools import zip_longest

def poll_instance_status(
    ec2_client,
    instance_id: str,
    desired_state: str,
    wait_interval: int = 5,
    timeout: int = 300,
):
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

    with yaspin(
        text=f"Waiting for instance {instance_id} to reach state '{desired_state}' (timeout {timeout}s)...",
        color="cyan",
    ) as spinner:
        while True:
            response = ec2_client.describe_instances(InstanceIds=[instance_id])
            state = response["Reservations"][0]["Instances"][0]["State"]["Name"]
            elapsed_time = time.time() - start_time

            if state == desired_state:
                spinner.ok("✅ ")
                click.echo(f"Instance {instance_id} is now '{desired_state}'.")
                break

            if elapsed_time > timeout:
                spinner.fail("💥 ")
                raise TimeoutError(
                    f"Timeout waiting for instance {instance_id} to reach '{desired_state}'. Last known state: {state}"
                )

            time.sleep(wait_interval)


def ec2_stop_instance(instance_id: str, region: str = "us-east-1", wait: bool = False):
    """
    Stop an EC2 instance and optionally wait until it is fully stopped.
    """
    ec2 = create_boto3_client("ec2", region)
    ec2.stop_instances(InstanceIds=[instance_id])

    if wait:
        poll_instance_status(ec2, instance_id, desired_state="stopped")


def ec2_start_instance(instance_id: str, region: str = "us-east-1", wait: bool = False):
    """
    Start an EC2 instance and optionally wait until it is fully running.
    """
    ec2 = create_boto3_client("ec2", region)
    ec2.start_instances(InstanceIds=[instance_id])

    if wait:
        poll_instance_status(ec2, instance_id, desired_state="running")


def ec2_update_instance_ip(instance_id: str, new_ip: str, region: str = "us-east-1"):
    """
    Update EC2 instance public IP address.
    """
    ec2 = create_boto3_client("ec2", region)
    ec2.modify_instance_attribute(
        InstanceId=instance_id, SourceDestCheck={"Value": False}
    )


def paginate_describe_instances(ec2_client) -> list:
    """
    Paginate through all EC2 instances in the region.

    Args:
        ec2_client (boto3.client): EC2 boto3 client.

    Returns:
        list: A list of EC2 instance dictionaries.
    """
    instances = []
    paginator = ec2_client.get_paginator("describe_instances")

    for page in paginator.paginate():
        for reservation in page.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                instances.append(
                    {
                        "InstanceId": instance.get("InstanceId"),
                        "State": instance.get("State", {}).get("Name"),
                        "InstanceType": instance.get("InstanceType"),
                        "PublicIpAddress": instance.get("PublicIpAddress"),
                        "PrivateIpAddress": instance.get("PrivateIpAddress"),
                        "LaunchTime": str(instance.get("LaunchTime")),
                    }
                )
    return instances


def ec2_list_all_instances(region: str = "us-east-1") -> list:
    """
    List all EC2 instances in the specified AWS region.
    """
    ec2 = create_boto3_client("ec2", region)

    with yaspin(text="Fetching EC2 instances...", color="cyan") as spinner:
        instances = paginate_describe_instances(ec2)
        spinner.ok("✅ ")

    return instances

def ec2_list_subnets(vpc_id: str, region: str = "us-east-1") -> list:
    _response_subnets = None
    with yaspin(text=f"Fetching subnets...", color="cyan",) as spinner:
        ec2 = create_boto3_client("ec2", region)
        response = ec2.describe_subnets(
            Filters=[
                {'Name': 'vpc-id', 'Values': [vpc_id]}
            ]
        )
        _response_subnets = response['Subnets']
        spinner.ok("✅ ")

    return _response_subnets

def ec2_get_available_cidr_blocks(
    vpc_id,
    target_prefix,
    num_blocks,
    region="us-east-1"
    ):
    """
    Returns a list of available CIDR blocks within the given VPC.

    Parameters:
        vpc_id (str): VPC identifier (used for logging/debugging).
        used_cidr_blocks (List[str]): List of currently used CIDRs.
        target_prefix (int): Desired prefix length for new blocks, e.g. 24.
        num_blocks (int): Number of available blocks to return.

    Returns:
        List[str]: List of available CIDR blocks as strings.
    """
    with yaspin(text=f"Fetching available CIDR blocks for VPC: {vpc_id}...", color="cyan") as spinner:
        
        ec2 = create_boto3_client("ec2", region)
        response1 = ec2.describe_subnets(
            Filters=[
                {'Name': 'vpc-id', 'Values': [vpc_id]}
            ]
        )
        used_cidr_blocks = [subnet['CidrBlock'] for subnet in response1['Subnets']]
        response2 = ec2.describe_vpcs(VpcIds=[vpc_id])
        vpc = response2['Vpcs'][0]
        vpc_cidr_block = vpc['CidrBlock']
        
        vpc_net = ipaddress.ip_network(vpc_cidr_block)
        used_networks = [ipaddress.ip_network(cidr) for cidr in used_cidr_blocks]

        used_networks.sort()
        used_networks_str = [str(net) for net in used_networks]

        all_candidates = list(vpc_net.subnets(new_prefix=target_prefix))
        available = []

        for candidate in all_candidates:
            if all(not candidate.overlaps(used) for used in used_networks):
                available.append(str(candidate))
            if len(available) >= num_blocks:
                break

        # _zip = list(zip_longest(used_networks_str, available, fillvalue="-"))
        # df = pd.DataFrame(_zip, columns=["Used CIDR Blocks", "Available CIDR Blocks"])
        df = pd.DataFrame(available, columns=["Available CIDR Blocks"])
        df.insert(0, "VPC ID", vpc_id)
        table_data = df.values.tolist()
        headers = df.columns.tolist()
        spinner.ok("✅ ")
    return table_data, headers