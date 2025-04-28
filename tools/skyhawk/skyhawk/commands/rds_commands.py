import click
import json
import csv
import os
from tabulate import tabulate
from skyhawk.repository import rds_start_instance
from skyhawk.repository import rds_stop_instance
from skyhawk.repository import rds_list_all_instances


@click.group()
def rds():
    """Commands to operate RDS instances."""
    pass


@rds.command(name="start-instance")
@click.option("--instance-id", required=True, help="ID of the RDS instance to start")
@click.option(
    "--wait",
    is_flag=True,
    default=False,
    help="Wait until RDS instance is fully available",
)
@click.option("--region", default="us-east-1", help="AWS region name")
def start_instance(instance_id: str, wait: bool, region: str):
    """
    Start an RDS DB instance by DB identifier.
    """
    rds_start_instance(instance_id, wait=wait, region=region)


@rds.command(name="stop-instance")
@click.option("--instance-id", required=True, help="ID of the RDS instance to stop")
@click.option(
    "--wait",
    is_flag=True,
    default=False,
    help="Wait until RDS instance is fully stopped",
)
@click.option("--region", default="us-east-1", help="AWS region name")
def stop_instance(instance_id: str, wait: bool, region: str):
    """
    Stop an RDS DB instance by DB identifier.
    """
    rds_stop_instance(instance_id, wait=wait, region=region)


@rds.command(name="list-instances")
@click.option(
    "--state",
    required=False,
    help="Filter instances by status (e.g., available, stopped)",
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
    List all RDS instances in the AWS region, optionally filtering by status.
    """
    instances = rds_list_all_instances(region=region)
    if not instances:
        click.echo("No RDS instances found.")
        return

    # Apply state filter if given
    if state:
        instances = [i for i in instances if i["DBInstanceStatus"] == state.lower()]
        if not instances:
            click.echo(f"No RDS instances found with status '{state}'.")
            return

    if output == "json":
        formatted_output = json.dumps(instances, indent=2)
    else:
        table_data = [
            [
                i.get("DBInstanceIdentifier", "-"),
                i.get("DBInstanceStatus", "-"),
                i.get("Engine", "-"),
                i.get("DBInstanceClass", "-"),
                i.get("Endpoint") or "-",
                i.get("AllocatedStorage") or "-",
                i.get("InstanceCreateTime", "-"),
            ]
            for i in instances
        ]
        headers = [
            "DBIdentifier",
            "Status",
            "Engine",
            "Class",
            "Endpoint",
            "Storage (GB)",
            "Created Time",
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
                        "DBInstanceIdentifier",
                        "DBInstanceStatus",
                        "Engine",
                        "DBInstanceClass",
                        "Endpoint",
                        "AllocatedStorage",
                        "InstanceCreateTime",
                    ],
                )
                writer.writeheader()
                writer.writerows(instances)
            click.echo(f"\nOutput saved to {save_path} (CSV format)")
