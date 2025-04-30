import os
import hashlib
import logging
import tempfile
from typing import Literal, Union, Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError
from botocore.config import Config
from render_rig.data_access.object_access.common_service import create_boto3_client
from urllib.parse import urlparse
import json

logger = logging.getLogger(__name__)

StorageMode = Literal["memory", "cache", "tempfile"]

def parse_s3_uri(s3_uri: str) -> tuple[str, str]:
    """
    Parse an S3 URI into bucket name and object key.

    :param s3_uri: Full S3 URI (e.g., 's3://bucket-name/path/to/object')
    :return: Tuple of (bucket_name, key)
    :raises ValueError: If the URI is invalid or doesn't start with 's3://'
    """
    parsed = urlparse(s3_uri)

    if parsed.scheme != "s3" or not parsed.netloc or not parsed.path:
        raise ValueError(f"Invalid S3 URI: {s3_uri}")

    bucket_name = parsed.netloc
    key = parsed.path.lstrip("/")  # Remove leading slash

    return bucket_name, key

def log_s3_download_attempt(bucket: str, key: str):
    print(f"[LOG] Attempting to download from S3: Bucket={bucket}, Key={key}")

def s3_get_object_by_bucket_key(
    bucket_name: str,
    key: str,
    region_name: str = "us-east-1",
    mode: StorageMode = "memory",  # 'memory', 'cache', or 'tempfile'
    cache_dir: str = "/tmp/s3_cache",
    s3_client: Optional[boto3.client] = None,
    max_retries: int = 3,
) -> Union[bytes, str]:
    """
    Download an object from S3 with flexible storage options.

    :param bucket_name: Name of the S3 bucket.
    :param key: Key of the object in the S3 bucket.
    :param region_name: AWS region of the bucket.
    :param mode: Where to store the file: 'memory' returns bytes, 'cache' or 'tempfile' returns path.
    :param cache_dir: Directory to store cache if using mode='cache'.
    :param s3_client: Optional boto3 client.
    :param max_retries: Retry attempts for S3 download.
    :return: bytes (memory) or str (file path for 'cache'/'tempfile')
    """
    if not bucket_name or not key:
        raise ValueError("Bucket name and key must be non-empty strings.")

    # Compute a safe cache filename
    cache_filename = hashlib.sha1(f"{bucket_name}/{key}".encode()).hexdigest()
    cache_path = os.path.join(cache_dir, cache_filename)

    if mode == "cache" and os.path.exists(cache_path):
        logger.info(f"Cache hit: {cache_path}")
        return cache_path

    if s3_client is None:
        s3_client = create_boto3_client("s3", region_name, max_retries)

    log_s3_download_attempt(bucket_name, key)

    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        data = response["Body"].read()
    except NoCredentialsError:
        logger.error("AWS credentials not found.")
        raise
    except (ClientError, EndpointConnectionError) as e:
        logger.error(f"S3 download error: {e}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error downloading from S3: {e}")
        raise

    # Handle storage mode
    if mode == "memory":
        return data
    elif mode == "cache":
        os.makedirs(cache_dir, exist_ok=True)
        with open(cache_path, "wb") as f:
            f.write(data)
        return cache_path
    elif mode == "tempfile":
        tf = tempfile.NamedTemporaryFile(delete=False)
        tf.write(data)
        tf.close()
        return tf.name
    else:
        raise ValueError(
            f"Invalid mode '{mode}'. Use 'memory', 'cache', or 'tempfile'."
        )

def s3_get_object_by_uri(
    s3_uri: Optional[str],
    region_name: str = "us-east-1",
    mode: StorageMode = "memory",
    cache_dir: str = "/tmp/s3_cache",
    s3_client: Optional[boto3.client] = None,
    max_retries: int = 3,
) -> Union[bytes, str]:
    """
    Download an object from S3 using a URI.

    :param s3_uri: Full S3 URI (e.g., 's3://bucket-name/path/to/object')
    :param region_name: AWS region of the bucket.
    :param mode: Where to store the file: 'memory', 'cache', or 'tempfile'.
    :param cache_dir: Directory to store cache if using mode='cache'.
    :param s3_client: Optional boto3 client.
    :param max_retries: Retry attempts for S3 download.
    :return: bytes (memory) or str (file path for 'cache'/'tempfile')
    :raises ValueError: If s3_uri is None or invalid.
    """
    if not s3_uri:
        raise ValueError("s3_uri must be a non-empty string.")

    bucket_name, key = parse_s3_uri(s3_uri)

    return s3_get_object_by_bucket_key(
        bucket_name=bucket_name,
        key=key,
        region_name=region_name,
        mode=mode,
        cache_dir=cache_dir,
        s3_client=s3_client,
        max_retries=max_retries,
    )

def s3_save_chart_json(
    chart_json_str: str,
    bucket_name: str,
    key: str,
    region_name: str = "us-east-1",
    s3_client: Optional[boto3.client] = None,
    max_retries: int = 3,
):
    """
    Save chart JSON to S3.

    :param chart_json_str: JSON string of the chart.
    :param bucket_name: S3 bucket name.
    :param key: S3 object key.
    :param region_name: AWS region.
    :param mode: Storage mode - memory, cache, or tempfile (currently unused).
    :param cache_dir: Directory to use if using cache mode (currently unused).
    :param s3_client: Optional pre-initialized boto3 S3 client.
    :param max_retries: Maximum number of retries for S3 client.
    """
    if s3_client is None:
        s3_client = create_boto3_client("s3", region_name, max_retries)

    try:
        s3_client.put_object(Bucket=bucket_name, Key=key, Body=chart_json_str)
        logger.info(f"Chart JSON saved to S3: Bucket={bucket_name}, Key={key}")
        return True
    except Exception as e:
        logger.error(f"Failed to save chart JSON to S3: {e}")
        return False

def s3_get_chart_json(
    bucket_name: str,
    key: str,
    region_name: str = "us-east-1",
    s3_client: Optional[boto3.client] = None,
    max_retries: int = 3,
) -> Optional[str]:
    """
    Retrieve chart JSON from S3.

    :param bucket_name: S3 bucket name.
    :param key: S3 object key.
    :param region_name: AWS region.
    :param s3_client: Optional pre-initialized boto3 S3 client.
    :param max_retries: Maximum number of retries for S3 client.
    :return: Chart JSON string or None if not found.
    """
    if s3_client is None:
        s3_client = create_boto3_client("s3", region_name, max_retries)

    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        chart_json = json.loads(response["Body"].read().decode("utf-8"))
        return chart_json
    except Exception as e:
        logger.error(f"Failed to retrieve chart JSON from S3: {e}")
        return None
    
if __name__ == "__main__":
    import datetime
    import json
    # Example usage
    uri = "s3://flight-px4-logs/raw-logs/2025/4/10/file_aaf83b7cd2644dbda8af648db3eabdfc.ulg"
    region_name = "us-east-1"

    try:
        data = s3_get_object_by_uri(s3_uri=uri, region_name=region_name, mode="cache")
        print(f"Downloaded data (first 100 bytes): {data[:100]}...")
    except Exception as e:
        logger.error(f"Failed to download object: {e}")

    bucket_name = "ypr-test-bucket-20250429"
    chart_json = {
        "log_ts_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "name": "example_chart",
    }
    chart_json_str = json.dumps(chart_json)

    now = datetime.datetime.now(datetime.timezone.utc)
    key = f"charts/{now.year}/{now.month}/{now.day}/example_chart.json"

    try:
        s3_save_chart_json(
            chart_json_str=chart_json_str,
            bucket_name=bucket_name,
            key=key,
            region_name=region_name,
        )
        logger.info(f"Chart JSON successfully saved to S3: {key}")
    except Exception as e:
        logger.error(f"Failed to save chart JSON to S3: {e}")