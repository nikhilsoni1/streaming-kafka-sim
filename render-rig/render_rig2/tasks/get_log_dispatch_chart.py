import os
import tempfile
from typing import Tuple
from botocore.exceptions import ClientError
from render_rig2.app import celery_app
from render_rig2.utils.logger import logger
from render_rig2.object_access.client import create_boto3_client
from render_rig2.utils.cache import cache
from ypr_core_logfoundry.parser import ULogParser
from render_rig2.chart_engine import CHART_REGISTRY
from render_rig2.chart_engine.manager import generate_chart_for_log
from render_rig2.utils.timing import timed_debug_log

def get_existing_log(bucket_name: str, key:str) -> ULogParser | None:
    """
    Downloads a .ulg file from S3 (non-GZIP), parses it using ULogParser, and returns structured output.

    Args:
        bucket_name (str): The name of the S3 bucket.
        key (str): The key of the file in the S3 bucket.

    Returns:
        Tuple[str, ULogParser] | None: (log_id, parsed_log) if successful, else None.
    """
    cache_key = f"{bucket_name}/{key}"

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
                with timed_debug_log(f"Downloading file - s3://{bucket_name}/{key}"):
                    s3.download_file(bucket_name, key, temp_file_path)

                logger.success(f"✅ Downloaded s3://{bucket_name}/{key} file to {temp_file_path}")
                with open(temp_file_path, "rb") as f:
                    file_bytes = f.read()
            finally:
                os.remove(temp_file_path)

            if file_bytes:
                expire = 5 * 60  # 5 minutes
                cache.set(cache_key, file_bytes, expire=expire)

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

            parsed_log = ULogParser(temp_file.name)

            logger.success(f"✅ Parsed ULog from s3://{bucket_name}/{key}")

            return parsed_log

    except Exception as e:
        logger.error(f"❌ Failed to parse ULog for {bucket_name}/{key}: {e}")
        return None


@celery_app.task(name="get_log_dispatch_chart")
def get_log_dispatch_chart(payload: Tuple[str, str, str], chart_name: str) -> str | None:
    """
    Dispatches a chart rendering task to the appropriate chart engine.
    
    Args:
        payload (Tuple[str, str, str]): A tuple containing:
            - log_id (str): Identifier for the log.
            - bucket_name (str): The name of the S3 bucket.
            - key (str): The key of the file in the S3 bucket.
        chart_name (str): Name of the chart to render.
    
    Returns:
        str | None: A JSON string representation of the rendered chart if successful, 
        otherwise None.
    """
    if payload is None:
        return None
    log_id, bucket_name, key = payload
    log_data = get_existing_log(bucket_name, key)
    if chart_name not in CHART_REGISTRY:
        logger.error(f"❌ Chart '{chart_name}' is not registered.")
        return None
    _chart = CHART_REGISTRY[chart_name]
    logger.info(f"🔧 Dispatching chart '{chart_name}' for log_id: {log_id}")
    with timed_debug_log(f"Chart delivery for {log_id} - {chart_name}"):
        chart_json = generate_chart_for_log(log_id, _chart, log_data)
    return chart_json