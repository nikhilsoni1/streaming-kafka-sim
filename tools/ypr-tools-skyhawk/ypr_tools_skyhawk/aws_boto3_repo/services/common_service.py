import boto3
from botocore.config import Config


def create_boto3_client(service_name: str, region_name: str = "us-west-2"):
    config = Config(retries={"max_attempts": 10, "mode": "standard"})
    return boto3.client(service_name, region_name=region_name, config=config)
