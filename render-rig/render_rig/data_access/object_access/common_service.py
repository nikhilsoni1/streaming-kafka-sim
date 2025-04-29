import boto3
import logging
from botocore.exceptions import BotoCoreError, NoRegionError, UnknownServiceError
from botocore.config import Config

logger = logging.getLogger(__name__)


def create_boto3_client(
    service: str, region_name: str = "us-east-1", max_retries: int = 3
):
    """
    Create a boto3 client with retry configuration and error handling.

    :param service: AWS service name (e.g., 's3', 'dynamodb').
    :param region_name: AWS region (e.g., 'us-east-1').
    :param max_retries: Number of retry attempts.
    :return: boto3 client instance.
    :raises: ValueError or BotoCoreError subclasses on failure.
    """
    if not service or not isinstance(service, str):
        raise ValueError("Service name must be a non-empty string.")
    if not region_name or not isinstance(region_name, str):
        raise ValueError("Region name must be a non-empty string.")
    if not isinstance(max_retries, int) or max_retries < 1:
        raise ValueError("max_retries must be a positive integer.")

    try:
        config = Config(retries={"max_attempts": max_retries, "mode": "standard"})
        client = boto3.client(service, region_name=region_name, config=config)
        return client
    except UnknownServiceError as e:
        logger.error(f"Unknown AWS service '{service}': {e}")
        raise
    except NoRegionError as e:
        logger.error(f"No region provided and none configured in environment: {e}")
        raise
    except BotoCoreError as e:
        logger.exception(
            f"Failed to create boto3 client for service '{service}' in region '{region_name}': {e}"
        )
        raise
