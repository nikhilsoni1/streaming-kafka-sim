import boto3
from render_rig2.utils.logger import logger
from botocore.exceptions import BotoCoreError, NoRegionError, UnknownServiceError
from botocore.config import Config
from render_rig2.utils.logger import logger
from render_rig2.utils.timing import timed_debug_log

_clients = {}  # Global cache


def create_boto3_client(
    service: str, region_name: str = "us-east-1", max_retries: int = 3
):
    """
    Create or reuse a boto3 client (singleton per service-region-retry combo).
    """
    key = (service, region_name, max_retries)
    if key in _clients:
        return _clients[key]

    if not service or not isinstance(service, str):
        logger.error("Service name must be a non-empty string.")
        raise ValueError("Service name must be a non-empty string.")
    if not region_name or not isinstance(region_name, str):
        logger.error("Region name must be a non-empty string.")
        raise ValueError("Region name must be a non-empty string.")
    if not isinstance(max_retries, int) or max_retries < 1:
        logger.error("max_retries must be a positive integer.")
        raise ValueError("max_retries must be a positive integer.")

    try:
        config = Config(retries={"max_attempts": max_retries, "mode": "standard"})
        with timed_debug_log(
            f"Creating boto3 client for service '{service}' in region '{region_name}'"
        ):
            client = boto3.client(service, region_name=region_name, config=config)
        _clients[key] = client
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
