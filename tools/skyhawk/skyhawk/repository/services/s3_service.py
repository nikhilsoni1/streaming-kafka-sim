# aws_repository/services/s3_service.py

import boto3
import click
from .common_service import create_boto3_client
from yaspin import yaspin
from botocore.exceptions import ClientError


def format_size(size_bytes: int) -> str:
    """Convert bytes to human-readable size."""
    if size_bytes < 1024:
        return f"{size_bytes} Bytes"
    elif size_bytes < 1024**2:
        return f"{round(size_bytes / 1024, 2)} KB"
    elif size_bytes < 1024**3:
        return f"{round(size_bytes / (1024**2), 2)} MB"
    elif size_bytes < 1024**4:
        return f"{round(size_bytes / (1024**3), 2)} GB"
    else:
        return f"{round(size_bytes / (1024**4), 2)} TB"


def format_object_count(count: int) -> str:
    """Convert object count to human-readable format."""
    if count < 1000:
        return f"{count}"
    elif count < 1_000_000:
        return f"{round(count / 1000, 1)}k"
    else:
        return f"{round(count / 1_000_000, 1)}M"


def s3_list_all_buckets(region: str = "us-east-1") -> dict:
    """
    List all S3 buckets with metrics like total objects and total size.
    """
    s3 = create_boto3_client("s3", region)
    s3_resource = boto3.resource("s3", region_name=region)

    buckets = []
    total_objects = 0
    total_size = 0  # in bytes

    with yaspin(text="Collecting S3 bucket metrics...", color="cyan") as spinner:
        try:
            response = s3.list_buckets()
            for bucket in response.get("Buckets", []):
                bucket_name = bucket["Name"]
                creation_date = str(bucket["CreationDate"])
                bucket_obj = s3_resource.Bucket(bucket_name)

                try:
                    obj_count = 0
                    size_bytes = 0
                    for obj in bucket_obj.objects.all():
                        obj_count += 1
                        size_bytes += obj.size

                    buckets.append(
                        {
                            "BucketName": bucket_name,
                            "CreationDate": creation_date,
                            "NumberOfObjects": format_object_count(obj_count),
                            "TotalSize": format_size(size_bytes),
                        }
                    )

                    total_objects += obj_count
                    total_size += size_bytes

                except Exception as e:
                    click.echo(f"Failed to access bucket {bucket_name}: {str(e)}")

            spinner.ok("✅ ")

        except Exception as e:
            spinner.fail("💥 ")
            raise e

    summary = {
        "total_objects": format_object_count(total_objects),
        "total_size": format_size(total_size),
    }

    return {"buckets": buckets, "summary": summary}
    """
    List all S3 buckets with metrics like total objects and total size.

    Args:
        region (str, optional): AWS region. Defaults to "us-east-1".

    Returns:
        dict: {
            "buckets": [bucket details...],
            "summary": {"total_objects": str, "total_size": str}
        }
    """
    s3 = create_boto3_client("s3", region)
    s3_resource = boto3.resource("s3", region_name=region)

    buckets = []
    total_objects = 0
    total_size = 0  # in bytes

    with click.spinner("Collecting S3 bucket metrics..."):
        response = s3.list_buckets()
        for bucket in response.get("Buckets", []):
            bucket_name = bucket["Name"]
            creation_date = str(bucket["CreationDate"])
            bucket_obj = s3_resource.Bucket(bucket_name)

            try:
                obj_count = 0
                size_bytes = 0
                for obj in bucket_obj.objects.all():
                    obj_count += 1
                    size_bytes += obj.size

                buckets.append(
                    {
                        "BucketName": bucket_name,
                        "CreationDate": creation_date,
                        "NumberOfObjects": format_object_count(obj_count),
                        "TotalSize": format_size(size_bytes),
                    }
                )

                total_objects += obj_count
                total_size += size_bytes

            except Exception as e:
                click.echo(f"Failed to access bucket {bucket_name}: {str(e)}")

    summary = {
        "total_objects": format_object_count(total_objects),
        "total_size": format_size(total_size),
    }

    return {"buckets": buckets, "summary": summary}


def s3_create_bucket(bucket_name: str, region: str = "us-east-1"):
    """Create a new S3 bucket."""
    s3 = create_boto3_client("s3", region)

    with yaspin(text=f"Creating bucket '{bucket_name}'...", color="cyan") as spinner:
        try:
            if region == "us-east-1":
                s3.create_bucket(Bucket=bucket_name)
            else:
                s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": region},
                )
            spinner.ok("✅ ")
            click.echo(f"Bucket '{bucket_name}' created successfully.")
        except ClientError as e:
            spinner.fail("💥 ")
            raise click.ClickException(
                f"Failed to create bucket: {e.response['Error']['Message']}"
            )


def s3_delete_bucket(bucket_name: str, region: str = "us-east-1"):
    """Delete an empty S3 bucket."""
    s3 = create_boto3_client("s3", region)

    with yaspin(text=f"Deleting bucket '{bucket_name}'...", color="cyan") as spinner:
        try:
            s3.delete_bucket(Bucket=bucket_name)
            spinner.ok("✅ ")
            click.echo(f"Bucket '{bucket_name}' deleted successfully.")
        except ClientError as e:
            spinner.fail("💥 ")
            raise click.ClickException(
                f"Failed to delete bucket: {e.response['Error']['Message']}"
            )
