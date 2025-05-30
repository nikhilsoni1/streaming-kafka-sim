import os
import tempfile
from typing import Tuple

from botocore.exceptions import ClientError
from ypr_core_logfoundry.parser import ULogParser

from render_rig2.app_v2 import celery_app
from render_rig2.chart_engine import CHART_REGISTRY
from render_rig2.chart_engine.manager import generate_chart_for_log
from render_rig2.contracts import TaskPayload
from render_rig2.object_access.client import create_boto3_client
from render_rig2.utils.cache import cache
from render_rig2.utils.logger import logger
from render_rig2.utils.redis_status import set_task_status


# TODO: Decouple this from ypr_core_logfoundry.parser
def get_existing_log(bucket_name: str, key: str) -> ULogParser | None:
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
        logger.info(f"Using cached file for {cache_key}")
    else:
        s3 = create_boto3_client("s3")
        logger.info(f"📥 Downloading s3://{bucket_name}/{key}...")

        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file_path = temp_file.name

            try:
                s3.download_file(bucket_name, key, temp_file_path)

                logger.success(
                    f"✅ Downloaded s3://{bucket_name}/{key} file to {temp_file_path}"
                )
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

            logger.success(f"Parsed ULog from s3://{bucket_name}/{key}")

            return parsed_log

    except Exception as e:
        logger.error(f"❌ Failed to parse ULog for {bucket_name}/{key}: {e}")
        return None


@celery_app.task(name="get_log_dispatch_chart", bind=True)
def get_log_dispatch_chart(self, payload_dict: dict) -> dict:
    """
    Dispatches a chart rendering task to the appropriate chart engine.

    Args:
        payload_dict (dict): Serialized TaskPayload.

    Returns:
        dict: Updated TaskPayload with result or error information.
    """
    # Validate and deserialize the payload dictionary
    payload = TaskPayload.model_validate(payload_dict)
    task_name = self.name
    payload.retries = self.request.retries
    payload.set_phase(
        "init_get_log_dispatch_chart", task_name=task_name, status="running"
    )

    # Step 1: Stop chain early if meta indicates so
    if payload.meta.get("stop_chain") is True:
        payload.set_phase("skipped_due_to_meta_flag", status="skipped")
        logger.info(
            f"[{payload.task_id}] {task_name} skipped due to meta['stop_chain']=True"
        )
        return payload.model_dump()

    chart_name = payload.chart_name
    log_id = payload.log_id

    try:
        # Step 2: Ensure previous task produced expected result
        payload.require_result_type("raw_log", expected_source="log_registry")
        bucket_name = payload.result.data.get("bucket_name")
        key = payload.result.data.get("key")

        # Step 3: Validate chart
        if chart_name not in CHART_REGISTRY:
            # Chain failure
            set_task_status(
                payload.task_id,
                {
                    "status": "failed",
                    "error": "Dispatch chart generation failed",
                },
            )
            error_msg = f"Chart '{chart_name}' is not registered."
            payload.log_error(error_msg)
            payload.set_phase("invalid_chart", status="failed")
            payload.meta["stop_chain"] = True
            logger.error(f"[{payload.task_id}] {error_msg}")
            return payload.model_dump()

        # Step 4: Generate chart
        _chart = CHART_REGISTRY[chart_name]
        logger.info(
            f"[{payload.task_id}] Dispatching chart '{chart_name}' for log_id: {log_id}"
        )
        log_data = get_existing_log(bucket_name, key)
        chart_json = generate_chart_for_log(log_id, _chart, log_data)
        payload.set_result(
            source="generated",
            type_="chart",
            data=chart_json,
        )
        payload.set_phase("chart_generated", status="success")
        # Line 138 - success
        set_task_status(payload.task_id, {
            "task_status": "success",
            "chart_status": "generated",
            "chart_json": chart_json
        })
    except Exception as e:
        # Chain failure
        set_task_status(
            payload.task_id,
            {
                "status": "failed",
                "error": "Dispatch chart generation failed",
            },
        )
        payload.log_error(e)
        payload.set_phase("chart_dispatch_error", status="failed")
        logger.exception(f"[{payload.task_id}] Exception in {task_name}")

    return payload.model_dump()
