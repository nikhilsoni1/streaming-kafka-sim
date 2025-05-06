import os
import tempfile
from time import perf_counter
from botocore.exceptions import ClientError

from render_rig2.app import celery_app
from render_rig2.logger import logger
from render_rig2.object_access.client import create_boto3_client
from ypr_core_logfoundry.parser import ULogParser


@celery_app.task(name="get_existing_log")
def get_existing_log(payload: tuple):
    """
    Downloads a .ulg file from S3 (non-GZIP), parses it using ULogParser, and returns structured output.

    Args:
        payload (tuple): (bucket_name: str, key: str)

    Returns:
        dict or None: Parsed ULog as dict if successful, otherwise None
    """
    try:
        bucket_name, key = payload
    except (TypeError, ValueError):
        logger.error("❌ Payload must be a tuple: (bucket_name, key)")
        return None

    s3 = create_boto3_client("s3")
    t0 = perf_counter()
    logger.info(f"📥 Downloading s3://{bucket_name}/{key} to temp file...")

    try:
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            s3.download_file(bucket_name, key, temp_file.name)
            logger.info(f"✅ File downloaded to {temp_file.name}")
            t1 = perf_counter()

            t2 = perf_counter()
            parsed_log = ULogParser(temp_file.name)
            t3 = perf_counter()
            logger.success(f"✅ ULog downloaded in {round(t1 - t0, 2)}s, parsed in {round(t3 - t2, 2)}s")

            if hasattr(parsed_log, "to_dict"):
                return parsed_log.to_dict()
            return parsed_log  # fallback if it's already a dict-like object

    except ClientError as e:
        logger.error(f"❌ S3 download failed for {bucket_name}/{key}: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to parse ULog from {bucket_name}/{key}: {e}")
        return None
