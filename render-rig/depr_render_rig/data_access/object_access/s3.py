import os
import json
import logging
import hashlib
import tempfile
from urllib.parse import urlparse
from typing import Literal, Union, Optional
import gzip
import boto3
from boto3.s3.transfer import TransferConfig
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError
import io
from depr_render_rig.utils.logger import log_function

logger = logging.getLogger(__name__)
StorageMode = Literal["memory", "cache", "tempfile"]

def parse_s3_uri(s3_uri: str) -> tuple[str, str]:
    """
    Parse an S3 URI into bucket name and object key.
    """
    parsed = urlparse(s3_uri)
    if parsed.scheme != "s3" or not parsed.netloc or not parsed.path:
        raise ValueError(f"Invalid S3 URI: {s3_uri}")
    return parsed.netloc, parsed.path.lstrip("/")

@log_function(log_return=False)
def s3_get_object_by_bucket_key(
    bucket_name: str,
    key: str,
    s3_client: Optional[boto3.client],
    mode: StorageMode = "memory",
    cache_dir: str = "/tmp/s3_cache",
) -> Union[bytes, str]:
    """
    Download an object from S3 with flexible storage options.
    Returns bytes for 'memory', and file path for 'cache' or 'tempfile'.
    """
    if not bucket_name or not key:
        logger.error("Bucket name or key is None or empty.")
        raise ValueError("Bucket name and key must be non-empty strings.")

    cache_filename = hashlib.sha1(f"{bucket_name}/{key}".encode()).hexdigest()
    cache_path = os.path.join(cache_dir, cache_filename)

    if mode == "cache" and os.path.exists(cache_path):
        logger.info(f"Cache hit: {cache_path}")
        return cache_path

    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        data = response["Body"].read()
        logger.info(f"Downloaded {len(data)} bytes from S3: Bucket={bucket_name}, Key={key}")
    except (NoCredentialsError, ClientError, EndpointConnectionError) as e:
        logger.error(f"S3 download error: {e}")
        raise
    except Exception as e:
        logger.exception("Unexpected error downloading from S3")
        raise

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
        raise ValueError(f"Invalid mode '{mode}'. Use 'memory', 'cache', or 'tempfile'.")

@log_function(log_return=False)
def s3_get_object_by_uri(
    s3_uri: Optional[str],
    s3_client: Optional[boto3.client],
    mode: StorageMode = "memory",
    cache_dir: str = "/tmp/s3_cache",
) -> Union[bytes, str]:
    """
    Download an object from S3 using a URI.
    """
    if not s3_uri:
        logger.error("s3_uri is None or empty.")
        raise ValueError("s3_uri must be a non-empty string.")
    bucket_name, key = parse_s3_uri(s3_uri)
    logger.info(f"Parsed S3 URI: Bucket={bucket_name}, Key={key}")
    return s3_get_object_by_bucket_key(
        bucket_name=bucket_name,
        key=key,
        mode=mode,
        cache_dir=cache_dir,
        s3_client=s3_client
    )

@log_function(log_return=False)
def s3_save_chart_json(
    chart_json_str: bytes,
    bucket_name: str,
    key: str,
    s3_client: Optional[boto3.client],
    use_transfer: bool = True,
    transfer_config: Optional[TransferConfig] = None,
    use_gzip: bool = True
) -> bool:
    """
    Save chart JSON (already UTF-8 encoded bytes) to S3 with optional gzip compression.
    """
    try:
        data = gzip.compress(chart_json_str) if use_gzip else chart_json_str

        extra_args = {
            "ContentEncoding": "gzip" if use_gzip else None,
            "ContentType": "application/json"
        }
        extra_args = {k: v for k, v in extra_args.items() if v is not None}

        if use_transfer:
            transfer_config = transfer_config or TransferConfig()
            s3_client.upload_fileobj(
                Fileobj=io.BytesIO(data),
                Bucket=bucket_name,
                Key=key,
                ExtraArgs=extra_args,
                Config=transfer_config
            )
            logger.info(f"Chart JSON saved to S3 using S3 Transfer: Bucket={bucket_name}, Key={key}, Gzip={use_gzip}")
        else:
            s3_client.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=data,
                **extra_args
            )
            logger.info(f"Chart JSON saved to S3 using put_object: Bucket={bucket_name}, Key={key}, Gzip={use_gzip}")
        return True
    except Exception as e:
        logger.error(f"Failed to save chart JSON to S3: {e}")
        return False

@log_function(log_return=False)
def s3_get_chart_json(
    bucket_name: str,
    key: str,
    s3_client: Optional[boto3.client]
) -> Optional[dict]:
    """
    Retrieve chart JSON from S3, handling optional gzip compression.
    """
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        raw_data = response["Body"].read()
        is_gzipped = response.get("ContentEncoding") == "gzip" or raw_data[:2] == b"\x1f\x8b"
        json_str = gzip.decompress(raw_data).decode("utf-8") if is_gzipped else raw_data.decode("utf-8")
        logger.info(f"Chart JSON retrieved from S3: Bucket={bucket_name}, Key={key}, Gzip={is_gzipped}")
        return json.loads(json_str)
    except Exception as e:
        logger.error(f"Failed to retrieve chart JSON from S3: {e}")
        return None

if __name__ == "__main__":
    pass
