import datetime
import gzip
import hashlib
import io
import os
import uuid
from typing import Optional

from boto3.s3.transfer import TransferConfig

from render_rig2.app_v2 import celery_app
from render_rig2.contracts import TaskPayload
from render_rig2.object_access.client import create_boto3_client
from render_rig2.utils.logger import logger


# rewrite the following function for a string inpiut instead of bytes
def hash_string_sha256(data: str) -> str:
    """
    Compute SHA-256 hash of a string.

    :param data: Input data as a string.
    :return: Hexadecimal SHA-256 hash string.
    """
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def generate_chart_metadata(log_id: str, chart_name: str, chart_json: dict) -> dict:
    """
    Generates metadata for a chart based on the log ID and chart name.

    Args:
        log_id (str): The log ID associated with the chart.
        chart_name (str): The name of the chart.
        chart_json (dict): The JSON representation of the chart.

    Returns:
        dict: A dictionary containing the metadata for the chart.
    """
    RENDER_RIG_CHARTS_BUCKET_NAME = os.getenv("RENDER_RIG_CHARTS_BUCKET_NAME", None)
    if RENDER_RIG_CHARTS_BUCKET_NAME is None:
        logger.error(
            "RENDER_RIG_CHARTS_BUCKET_NAME is not set in the environment variables."
        )
        return None

    _now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    log_ts_utc = _now
    upd_ts_utc = _now
    _log_id = log_id
    chart_id = str(uuid.uuid4().hex)
    chart_name = chart_name
    chart_hash_sha256 = hash_string_sha256(chart_json)
    key = f"charts/{_log_id}/{chart_name}/{chart_id}.json"
    bucket_name = RENDER_RIG_CHARTS_BUCKET_NAME

    chart_metadata = {
        "log_id": _log_id,
        "chart_name": chart_name,
        "chart_id": chart_id,
        "chart_hash_sha256": chart_hash_sha256,
        "bucket_name": bucket_name,
        "key": key,
        "log_ts_utc": log_ts_utc,
        "upd_ts_utc": upd_ts_utc,
    }
    logger.success(f"Chart metadata generated successfully")
    return chart_metadata


def save_chart_json_to_s3(
    chart_json: str,
    bucket_name: str,
    key: str,
    use_transfer: bool = True,
    transfer_config: Optional[TransferConfig] = None,
    use_gzip: bool = True,
) -> bool:
    """
    Saves the chart JSON to S3.
    Args:
        chart_json (str): The JSON representation of the chart.
        bucket_name (str): The name of the S3 bucket.
        key (str): The key under which to store the chart JSON.
        use_transfer (bool): Whether to use S3 Transfer for uploading.
        transfer_config (TransferConfig, optional): Transfer configuration for S3 Transfer.
        use_gzip (bool): Whether to compress the data using gzip.
    Returns:
        bool: True if the upload was successful, False otherwise.
    """
    s3_client = create_boto3_client("s3")
    try:
        chart_json = (
            chart_json.encode("utf-8") if isinstance(chart_json, str) else chart_json
        )
        data = gzip.compress(chart_json) if use_gzip else chart_json

        extra_args = {
            "ContentEncoding": "gzip" if use_gzip else None,
            "ContentType": "application/json",
        }
        extra_args = {k: v for k, v in extra_args.items() if v is not None}

        if use_transfer:
            transfer_config = transfer_config or TransferConfig()
            s3_client.upload_fileobj(
                Fileobj=io.BytesIO(data),
                Bucket=bucket_name,
                Key=key,
                ExtraArgs=extra_args,
                Config=transfer_config,
            )
            logger.info(
                f"Chart JSON saved to S3 using S3 Transfer: Bucket={bucket_name}, Key={key}, Gzip={use_gzip}"
            )
        else:
            s3_client.put_object(Bucket=bucket_name, Key=key, Body=data, **extra_args)
            logger.info(
                f"Chart JSON saved to S3 using put_object: Bucket={bucket_name}, Key={key}, Gzip={use_gzip}"
            )
        return True
    except Exception as e:
        logger.error(f"Failed to save chart JSON to S3: {e}")
        return False


@celery_app.task(name="store_chart_json_in_s3", bind=True)
def store_chart_json_in_s3(self, payload_dict: dict) -> dict:
    """
    Stores the generated chart JSON in S3 using chart metadata.

    Args:
        payload_dict (dict): Serialized TaskPayload containing chart JSON.

    Returns:
        dict: Updated TaskPayload with result or error information.
    """

    # Validate and deserialize the payload dictionary
    payload = TaskPayload.model_validate(payload_dict)
    task_name = self.name
    payload.retries = self.request.retries
    payload.set_phase("init_store_chart_json", task_name=task_name, status="running")

    # Step 1: Stop chain early if meta indicates so
    if payload.meta.get("stop_chain") is True:
        payload.set_phase("skipped_due_to_meta_flag", status="skipped")
        logger.info(
            f"[{payload.task_id}] {task_name} skipped due to meta['stop_chain']=True"
        )
        return payload.model_dump()

    try:
        log_id = payload.log_id
        chart_name = payload.chart_name

        # Step 2: Ensure previous result has the generated chart
        payload.require_result_type("chart", expected_source="generated")
        chart_json = payload.result.data

        # Step 3: Generate chart metadata
        chart_metadata = generate_chart_metadata(log_id, chart_name, chart_json)
        if chart_metadata is None:
            error_msg = "Failed to generate chart metadata. Aborting S3 upload."
            payload.log_error(error_msg)
            payload.set_phase("metadata_generation_failed", status="skipped")
            logger.error(f"[{payload.task_id}] {error_msg}")
            return payload.model_dump()

        # Step 4: Upload to S3
        bucket_name = chart_metadata["bucket_name"]
        key = chart_metadata["key"]
        upload_success = save_chart_json_to_s3(
            chart_json=chart_json, bucket_name=bucket_name, key=key
        )

        if upload_success:
            payload.set_result(source="s3", type_="reference", data=chart_metadata)
            payload.set_phase("chart_json_stored", status="success")
        else:
            payload.log_error("S3 upload failed.")
            payload.set_phase("s3_upload_failed", status="failed")

    except Exception as e:
        payload.log_error(e)
        payload.set_phase("store_chart_exception", status="failed")
        logger.exception(f"[{payload.task_id}] Exception in {task_name}")

    return payload.model_dump()
