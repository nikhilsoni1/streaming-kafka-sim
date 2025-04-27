import click
import json
import csv
import os
from tabulate import tabulate

from aws_repository import ec2_start_instance
from aws_repository import ec2_stop_instance
from aws_repository import ec2_update_instance_ip
from aws_repository import ec2_list_all_instances


@click.group()
def ec2():
    """Commands to operate EC2 instances."""
    pass


@ec2.command(name="stop-instance")
@click.option("--instance-id", required=True, help="ID of the EC2 instance to stop")
@click.option(
    "--wait", is_flag=True, default=False, help="Wait until instance is fully stopped"
)
@click.option("--region", default="us-east-1", help="AWS region name")
def stop_instance(instance_id: str, wait: bool, region: str):
    """
    Stop an EC2 instance by Instance ID.
    """
    ec2_stop_instance(instance_id, wait=wait, region=region)


@ec2.command(name="start-instance")
@click.option("--instance-id", required=True, help="ID of the EC2 instance to start")
@click.option(
    "--wait", is_flag=True, default=False, help="Wait until instance is fully running"
)
@click.option("--region", default="us-east-1", help="AWS region name")
def start_instance(instance_id: str, wait: bool, region: str):
    """
    Start an EC2 instance by Instance ID.
    """
    ec2_start_instance(instance_id, wait=wait, region=region)


@ec2.command(name="update-ip")
@click.option("--instance-id", required=True, help="ID of the EC2 instance to update")
@click.option("--new-ip", required=True, help="New public IP address")
@click.option("--region", default="us-east-1", help="AWS region name")
def update_ip(instance_id: str, new_ip: str, region: str):
    """
    Update the public IP address of an EC2 instance.
    """
    ec2_update_instance_ip(instance_id, new_ip, region=region)


@ec2.command(name="list-instances")
@click.option(
    "--state", required=False, help="Filter instances by state (e.g., running, stopped)"
)
@click.option(
    "--output",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format: table or json",
)
@click.option("--region", default="us-east-1", help="AWS region name")
@click.option(
    "--save-path",
    required=False,
    help="File path to save output (CSV or JSON based on format)",
)
def list_instances(
    state: str = None,
    output: str = "table",
    region: str = "us-east-1",
    save_path: str = None,
):
    """
    List all EC2 instances in the AWS region, optionally filtering by state.
    """
    instances = ec2_list_all_instances(region=region)
    if not instances:
        click.echo("No EC2 instances found.")
        return

    # Apply state filter if given
    if state:
        instances = [i for i in instances if i["State"] == state.lower()]
        if not instances:
            click.echo(f"No EC2 instances found with state '{state}'.")
            return

    if output == "json":
        formatted_output = json.dumps(instances, indent=2)
    else:
        table_data = [
            [
                i.get("InstanceId", "-"),
                i.get("State", "-"),
                i.get("InstanceType", "-"),
                i.get("PublicIpAddress") or "-",
                i.get("PrivateIpAddress") or "-",
                i.get("LaunchTime", "-"),
            ]
            for i in instances
        ]
        headers = [
            "InstanceId",
            "State",
            "Type",
            "Public IP",
            "Private IP",
            "Launch Time",
        ]
        formatted_output = tabulate(table_data, headers=headers, tablefmt="pretty")

    click.echo(formatted_output)

    # Saving if save-path given
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        if output == "json":
            with open(save_path, "w") as f:
                json.dump(instances, f, indent=2)
            click.echo(f"\nOutput saved to {save_path} (JSON format)")
        elif output == "table":
            with open(save_path, "w", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "InstanceId",
                        "State",
                        "InstanceType",
                        "PublicIpAddress",
                        "PrivateIpAddress",
                        "LaunchTime",
                    ],
                )
                writer.writeheader()
                writer.writerows(instances)
            click.echo(f"\nOutput saved to {save_path} (CSV format)")
