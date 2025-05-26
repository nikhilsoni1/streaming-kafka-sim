import json
import gzip
import io
from botocore.exceptions import ClientError
from render_rig2.app import celery_app
from render_rig2.utils.logger import logger
from render_rig2.object_access.client import create_boto3_client
from typing import Optional, Tuple
from render_rig2.utils.timing import timed_debug_log


@celery_app.task(name="get_existing_chart")
def get_existing_chart(payload: Tuple[str, str, str]) -> Optional[dict]:
    """
    Fetches and parses a GZIP-compressed JSON object from S3.

    Args:
        payload (Tuple[str, str]): A tuple containing the bucket name and key of the S3 object.

    Returns:
        dict: Parsed JSON content if object exists, else None
    """
    if payload is None:
        return None

    log_id, bucket_name, key = payload

    if not bucket_name or not key:
        logger.error("❌ Invalid payload: missing 'bucket_name' or 'key'")
        return None

    s3 = create_boto3_client("s3")
    logger.info(f"📥 Fetching GZIP-compressed object: s3://{bucket_name}/{key}")

    try:

        with timed_debug_log(
            "Downloading and decompressing GZIP JSON - {log_id} - s3://{bucket_name}/{key}"
        ):
            s3_obj = s3.get_object(Bucket=bucket_name, Key=key)
            compressed_data = s3_obj["Body"].read()
            with gzip.GzipFile(fileobj=io.BytesIO(compressed_data)) as gz:
                decompressed = gz.read()

        logger.success(
            f"✅ Parsed GZIP JSON for {log_id}, type {str(type(decompressed))}"
        )
        return decompressed

    except ClientError as e:
        if e.response["Error"]["Code"] in ("404", "NoSuchKey"):
            logger.warning(f"🛑 Object not found: s3://{bucket_name}/{key}")
            return None
        else:
            logger.error(f"❌ S3 error: {e}")
            raise
    except Exception as e:
        logger.error(f"❌ Failed to parse GZIP JSON from s3://{bucket_name}/{key}: {e}")
        raise
