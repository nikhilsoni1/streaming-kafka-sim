import time
from yaspin import yaspin
import click
from .common_service import create_boto3_client


def get_rds_instance_status(rds_client, db_instance_id: str) -> str:
    """
    Fetch the current status of a DB instance.
    """
    response = rds_client.describe_db_instances(DBInstanceIdentifier=db_instance_id)
    return response["DBInstances"][0]["DBInstanceStatus"]


def paginate_describe_db_instances(rds_client) -> list:
    """
    Paginate through all RDS DB instances in the region.
    """
    instances = []
    paginator = rds_client.get_paginator("describe_db_instances")

    for page in paginator.paginate():
        for db_instance in page.get("DBInstances", []):
            instances.append(
                {
                    "DBInstanceIdentifier": db_instance.get("DBInstanceIdentifier"),
                    "DBInstanceStatus": db_instance.get("DBInstanceStatus"),
                    "Engine": db_instance.get("Engine"),
                    "DBInstanceClass": db_instance.get("DBInstanceClass"),
                    "Endpoint": db_instance.get("Endpoint", {}).get("Address"),
                    "AllocatedStorage": db_instance.get("AllocatedStorage"),
                    "InstanceCreateTime": str(db_instance.get("InstanceCreateTime")),
                }
            )
    return instances


def poll_rds_instance_status(
    rds_client,
    db_instance_id: str,
    desired_status: str,
    wait_interval: int = 10,
    timeout: int = 600,
):
    """
    Poll the RDS instance status until it reaches the desired status, or timeout occurs.
    """
    start_time = time.time()

    with yaspin(
        text=f"Waiting for RDS instance {db_instance_id} to reach status '{desired_status}' (timeout {timeout}s)...",
        color="cyan",
    ) as spinner:
        while True:
            current_status = get_rds_instance_status(rds_client, db_instance_id)
            elapsed_time = time.time() - start_time

            if current_status == desired_status:
                spinner.ok("✅ ")
                click.echo(f"RDS instance {db_instance_id} is now '{desired_status}'.")
                break

            if elapsed_time > timeout:
                spinner.fail("💥 ")
                raise TimeoutError(
                    f"Timeout waiting for RDS instance {db_instance_id} to reach '{desired_status}'. Last known status: {current_status}"
                )

            time.sleep(wait_interval)


def rds_start_instance(db_id: str, region: str = "us-east-1", wait: bool = False):
    """
    Start an RDS DB instance and optionally wait until it is available.
    Only starts if instance is currently 'stopped'.
    """
    rds = create_boto3_client("rds", region)
    current_status = get_rds_instance_status(rds, db_id)

    if current_status == "available":
        click.echo(f"RDS instance {db_id} is already 'available'. No action needed.")
    elif current_status == "stopped":
        click.echo(f"Starting RDS instance {db_id}...")
        rds.start_db_instance(DBInstanceIdentifier=db_id)
        if wait:
            poll_rds_instance_status(rds, db_id, desired_status="available")
    else:
        click.echo(
            f"Cannot start RDS instance {db_id}. Current state: '{current_status}'. Start aborted."
        )


def rds_stop_instance(db_id: str, region: str = "us-east-1", wait: bool = False):
    """
    Stop an RDS DB instance and optionally wait until it is stopped.
    Only stops if instance is currently 'available'.
    """
    rds = create_boto3_client("rds", region)
    current_status = get_rds_instance_status(rds, db_id)

    if current_status == "stopped":
        click.echo(f"RDS instance {db_id} is already 'stopped'. No action needed.")
    elif current_status == "available":
        click.echo(f"Stopping RDS instance {db_id}...")
        rds.stop_db_instance(DBInstanceIdentifier=db_id)
        if wait:
            poll_rds_instance_status(rds, db_id, desired_status="stopped")
    else:
        click.echo(
            f"Cannot stop RDS instance {db_id}. Current state: '{current_status}'. Stop aborted."
        )


def rds_list_all_instances(region: str = "us-east-1") -> list:
    """
    List all RDS DB instances in the specified AWS region.
    """
    rds = create_boto3_client("rds", region)

    with yaspin(text="Fetching RDS instances...", color="cyan") as spinner:
        instances = paginate_describe_db_instances(rds)
        spinner.ok("✅ ")

    return instances

def rds_reboot_instance(db_id: str, region: str = "us-east-1", wait: bool = False):
    """
    Reboot an RDS DB instance and optionally wait until it is available again.
    Only reboots if the instance is currently 'available'.
    """
    rds = create_boto3_client("rds", region)
    current_status = get_rds_instance_status(rds, db_id)

    if current_status != "available":
        click.echo(
            f"Cannot reboot RDS instance {db_id}. Current state: '{current_status}'. Reboot aborted."
        )
        return

    click.echo(f"Rebooting RDS instance {db_id}...")
    rds.reboot_db_instance(DBInstanceIdentifier=db_id)

    if wait:
        poll_rds_instance_status(rds, db_id, desired_status="available")
