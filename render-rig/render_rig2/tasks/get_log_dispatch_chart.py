import os
import tempfile
from time import perf_counter
from typing import Tuple
from botocore.exceptions import ClientError
from render_rig2.app import celery_app
from render_rig2.utils.logger import logger
from render_rig2.object_access.client import create_boto3_client
from render_rig2.utils.cache import cache
from ypr_core_logfoundry.parser import ULogParser
from render_rig2.chart_engine import CHART_REGISTRY
from render_rig2.chart_engine.manager import generate_chart_for_log


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
    log_id, bucket_name, key = payload
    log_data = get_existing_log(bucket_name, key)
    if chart_name not in CHART_REGISTRY:
        logger.error(f"❌ Chart '{chart_name}' is not registered.")
        return None
    _chart = CHART_REGISTRY[chart_name]
    logger.info(f"🔧 Dispatching chart '{chart_name}' for log_id: {log_id}")
    chart_json = generate_chart_for_log(log_id, _chart, log_data)
    return chart_json