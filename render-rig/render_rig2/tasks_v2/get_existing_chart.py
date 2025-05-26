import json
import gzip
import io
from botocore.exceptions import ClientError
from render_rig2.app import celery_app
from render_rig2.utils.logger import logger
from render_rig2.object_access.client import create_boto3_client
from render_rig2.contracts import TaskPayload


@celery_app.task(
    name="get_existing_chart",
    bind=True,
)
def get_existing_chart(self, payload_dict: dict) -> dict:
    """
    Fetches and parses a GZIP-compressed JSON object from S3.

    Args:
        payload (Tuple[str, str]): A tuple containing the bucket name and key of the S3 object.

    Returns:
        dict: Parsed JSON content if object exists, else None
    """
    payload = TaskPayload.model_validate(payload_dict)
    task_name = self.name
    payload.set_phase("getting_existing_chart_from_s3", task_name=task_name, status="running")

    if payload.result is None:
        logger.warning(f"[{payload.task_id}] No chart reference found. Skipping {task_name}.")
        payload.set_phase("skipped_get_existing_chart", status="skipped")
        return payload.model_dump()


    bucket_name = payload.result.data.get("bucket_name")
    key = payload.result.data.get("key")
    log_id = payload.log_id

    if not bucket_name or not key:
        logger.error(f"[{payload.task_id}] Missing bucket_name or key in result payload")
        payload.log_error("Missing bucket_name or key in result payload.")
        payload.set_phase("invalid_s3_reference", status="failed")
        return payload.model_dump()

    s3 = create_boto3_client("s3")
    logger.info(f"[{payload.task_id}] Fetching GZIP JSON from s3://{bucket_name}/{key}")

    try:
        s3_obj = s3.get_object(Bucket=bucket_name, Key=key)
        compressed_data = s3_obj["Body"].read()
        with gzip.GzipFile(fileobj=io.BytesIO(compressed_data)) as gz:
            decompressed = gz.read()

        payload.set_result(
            source="s3",
            type_="chart",
            data=decompressed
        )
        payload.set_phase("fetched_existing_chart", status="success")
        payload.meta["stop_chain"] = True
        logger.success(
            f"[{payload.task_id}] Parsed GZIP JSON for {log_id}, type {str(type(decompressed))}"
        )
    except ClientError as e:
        if e.response["Error"]["Code"] in ("404", "NoSuchKey"):
            logger.warning(f"[{payload.task_id}] Chart not found in S3: s3://{bucket_name}/{key}")
            payload.result = None
            payload.set_phase("chart_missing_in_s3", status="need_generation")
        else:
            payload.log_error(e)
            payload.set_phase("s3_error", status="failed")
            raise
    except Exception as e:
        payload.log_error(e)
        payload.set_phase("decompression_error", status="failed")
        logger.exception(f"[{payload.task_id}] Failed to decompress chart from S3")
        raise

    return payload.model_dump()
