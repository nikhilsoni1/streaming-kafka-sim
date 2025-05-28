import gzip
import io
import json

from botocore.exceptions import ClientError

from render_rig2.app_v2 import celery_app
from render_rig2.contracts import TaskPayload
from render_rig2.object_access.client import create_boto3_client
from render_rig2.utils.logger import logger
from render_rig2.utils.redis_status import set_task_status


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
    # Validate and deserialize the payload dictionary
    payload = TaskPayload.model_validate(payload_dict)
    task_name = self.name
    payload.set_phase("init_get_existing_chart", task_name=task_name, status="running")

    # Check if the task should be skipped
    if payload.result is None:
        logger.warning(
            f"[{payload.task_id}] No chart reference found. Skipping {task_name}."
        )
        payload.set_phase("skipped_get_existing_chart", status="running")
        return payload.model_dump()

    # Extract bucket name and key from the payload result
    bucket_name = payload.result.data.get("bucket_name")
    key = payload.result.data.get("key")
    log_id = payload.log_id
    s3 = create_boto3_client("s3")
    logger.info(f"[{payload.task_id}] Fetching GZIP JSON from s3://{bucket_name}/{key}")

    try:
        # Fetch the GZIP-compressed JSON object from S3
        s3_obj = s3.get_object(Bucket=bucket_name, Key=key)
        compressed_data = s3_obj["Body"].read()
        with gzip.GzipFile(fileobj=io.BytesIO(compressed_data)) as gz:
            decompressed = gz.read()
        payload.set_result(source="s3", type_="chart", data=decompressed)

        # Mark the task as successfully fetched and stop the chain
        payload.set_phase("fetched_existing_chart", status="success")

        status_dict = dict()
        status_dict["task_status"] = "success"
        status_dict["chart_status"] = "cached"
        status_dict["chart_json"] = decompressed.decode("utf-8")

        logger.info(
            f"[{payload.task_id}] Set task to be fired"
        )
        set_task_status(task_id=payload.task_id, status_dict=status_dict)
        logger.info(
            f"[{payload.task_id}] Set task fired"
        )
        payload.meta["stop_chain"] = True
        logger.success(
            f"[{payload.task_id}] Parsed GZIP JSON for {log_id}, type {str(type(decompressed))}"
        )
    except ClientError as e:
        # Specified bucket or key does not exist in S3
        if e.response["Error"]["Code"] in ("404", "NoSuchKey"):
            logger.warning(
                f"[{payload.task_id}] Chart not found in S3: s3://{bucket_name}/{key}"
            )
            payload.result = None
            payload.set_phase("chart_missing_in_s3", status="running")
        else:
            payload.log_error(e)
            payload.set_phase("s3_error", status="running")
            raise
    except Exception as e:
        payload.log_error(e)
        payload.set_phase("decompression_error", status="running")
        logger.exception(f"[{payload.task_id}] Failed to decompress chart from S3")
        raise

    return payload.model_dump()
