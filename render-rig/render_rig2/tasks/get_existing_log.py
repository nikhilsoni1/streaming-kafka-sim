import os
import tempfile
from time import perf_counter
from botocore.exceptions import ClientError

from render_rig2.app import celery_app
from render_rig2.logger import logger
from render_rig2.object_access.client import create_boto3_client
from render_rig2.cache import cache
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
        cache_key = f"{bucket_name}/{key}"
    except (TypeError, ValueError):
        logger.error("❌ Payload must be a tuple: (bucket_name, key)")
        return None

    file_bytes = cache.get(cache_key)

    if isinstance(file_bytes, bytes) and file_bytes:
        logger.info(f"⚡ Using cached file for {cache_key}")
    else:
        s3 = create_boto3_client("s3")
        logger.info(f"📥 Downloading s3://{bucket_name}/{key}...")

        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file_path = temp_file.name

            try:
                t0_download_file = perf_counter()
                s3.download_file(bucket_name, key, temp_file_path)
                t1_download_file = perf_counter()
                logger.info(f"✅ Downloaded {key} in {round(t1_download_file - t0_download_file, 2)}s")

                with open(temp_file_path, "rb") as f:
                    file_bytes = f.read()
            finally:
                os.remove(temp_file_path)

            if file_bytes:
                cache.set(cache_key, file_bytes, expire=86400)  # 1-day expiry
                logger.info(f"✅ File cached for {cache_key}")
            else:
                logger.error(f"❌ Downloaded file is empty: {cache_key}")
                return None

        except ClientError as e:
            logger.error(f"❌ S3 download failed for {bucket_name}/{key}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error during S3 download: {e}")
            return None

    # Parse from downloaded/cached bytes
    try:
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            temp_file.write(file_bytes)
            temp_file.flush()

            t_parse_start = perf_counter()
            parsed_log = ULogParser(temp_file.name)
            t_parse_end = perf_counter()

            logger.success(f"✅ Parsed ULog in {round(t_parse_end - t_parse_start, 2)}s")

            return parsed_log.to_dict() if hasattr(parsed_log, "to_dict") else parsed_log

    except Exception as e:
        logger.error(f"❌ Failed to parse ULog for {bucket_name}/{key}: {e}")
        return None
