import click
import json
import csv
import os
from tabulate import tabulate
from skyhawk.repository import s3_list_all_buckets
from skyhawk.repository import s3_create_bucket
from skyhawk.repository import s3_delete_bucket

@click.group()
def s3():
    """Commands to operate S3 buckets."""
    pass


@s3.command(name="list-buckets")
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
def list_buckets(
    output: str = "table", region: str = "us-east-1", save_path: str = None
):
    """
    List all S3 buckets with metrics (object count, total size).
    """
    result = s3_list_all_buckets(region=region)
    buckets = result["buckets"]
    summary = result["summary"]

    if not buckets:
        click.echo("No S3 buckets found or accessible.")
        return

    if output == "json":
        formatted_output = json.dumps(result, indent=2)
    else:
        table_data = [
            [
                b.get("BucketName", "-"),
                b.get("CreationDate", "-"),
                b.get("NumberOfObjects", "-"),
                b.get("TotalSize", "-"),
            ]
            for b in buckets
        ]
        headers = ["Bucket Name", "Creation Date", "Number of Objects", "Total Size"]
        formatted_output = tabulate(table_data, headers=headers, tablefmt="pretty")

        # Add summary row in terminal (only for table mode)
        formatted_output += (
            f"\n\nSummary:\n"
            f"Total Buckets: {len(buckets)}\n"
            f"Total Objects: {summary['total_objects']}\n"
            f"Total Size: {summary['total_size']}"
        )

    click.echo(formatted_output)

    # Saving if save-path given
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        if output == "json":
            with open(save_path, "w") as f:
                json.dump(result, f, indent=2)
            click.echo(f"\nOutput saved to {save_path} (JSON format)")

        elif output == "table":
            with open(save_path, "w", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "BucketName",
                        "CreationDate",
                        "NumberOfObjects",
                        "TotalSize",
                    ],
                )
                writer.writeheader()
                writer.writerows(buckets)
            click.echo(f"\nOutput saved to {save_path} (CSV format)")


@s3.command(name="create-bucket")
@click.option("--bucket-name", required=True, help="Name of the S3 bucket to create")
@click.option("--region", default="us-east-1", help="AWS region name")
def create_bucket(bucket_name: str, region: str):
    """
    Create a new S3 bucket.
    """
    s3_create_bucket(bucket_name, region)


@s3.command(name="delete-bucket")
@click.option("--bucket-name", required=True, help="Name of the S3 bucket to delete")
@click.option("--region", default="us-east-1", help="AWS region name")
def delete_bucket(bucket_name: str, region: str):
    """
    Delete an empty S3 bucket.
    """
    s3_delete_bucket(bucket_name, region)
