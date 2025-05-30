from typing import Tuple
from urllib.parse import urlparse

from sqlalchemy.exc import SQLAlchemyError

from render_rig2.app_v2 import celery_app
from render_rig2.contracts import TaskPayload
from render_rig2.database_access.models.log_registry_model import LogsDlReg
from render_rig2.database_access.sessions.log_registry_session_local import (
    LogRegistrySessionLocal,
)
from render_rig2.utils.logger import logger
from render_rig2.utils.redis_status import set_task_status


def parse_s3_uri(s3_uri: str) -> Tuple[str, str]:
    """
    Extracts the bucket and key from an S3 URI.

    Args:
        s3_uri (str): e.g., "s3://bucket-name/path/to/file.ext"

    Returns:
        Tuple[str, str]: (bucket_name, key)
    """
    if not s3_uri.startswith("s3://"):
        logger.error("Invalid S3 URI. Must start with 's3://'.")
        raise ValueError("Invalid S3 URI. Must start with 's3://'.")
    parsed = urlparse(s3_uri)
    bucket = parsed.netloc
    key = parsed.path.lstrip("/")
    return bucket, key


@celery_app.task(name="lookup_log_registry", bind=True)
def lookup_log_registry(self, payload_dict: dict) -> dict:
    """
    Looks up the log in the LogRegistry by log_id.

    Args:
        payload_dict (dict): Serialized TaskPayload dictionary.

    Returns:
        dict: Updated TaskPayload with result (if found) or phase/status updates.
    """
    # Validate and deserialize the payload dictionary
    payload = TaskPayload.model_validate(payload_dict)
    log_id = payload.log_id
    task_name = self.name

    payload.set_phase(
        phase="init_lookup_log_registry", task_name=task_name, status="running"
    )

    # Check if the task should be skipped based on meta flags
    if payload.meta.get("stop_chain") is True:
        payload.set_phase("skipped_due_to_meta_flag", status="skipped")
        logger.info(
            f"[{payload.task_id}] {task_name} skipped due to meta['stop_chain']=True"
        )
        return payload.model_dump()

    payload.set_phase("looking_up_log_registry", task_name=task_name, status="running")
    db = LogRegistrySessionLocal()
    try:
        result = (
            db.query(
                LogsDlReg.file_s3_path,
            )
            .filter_by(log_id=log_id)
            .first()
        )

        if result:
            logger.success(f"Found log registry entry for {log_id}")
            bucket_name, key = parse_s3_uri(result.file_s3_path)
            payload.set_result(
                source="log_registry",
                type_="raw_log",
                data={
                    "log_id": payload.log_id,
                    "bucket_name": bucket_name,
                    "key": key,
                },
            )
            payload.set_phase("log_found_in_registry", status="running")
        else:
            # Chain failure

            set_task_status(
                task_id=payload.task_id,
                status_dict={
                    "task_status": "failed",
                    "log_status": "not_found",
                    "log_id": log_id,
                },
            )

            payload.result = None
            payload.set_phase("log_not_found_in_registry", status="failed")
            payload.meta["stop_chain"] = True
            logger.error(f"Lookup ok but no log entry found in registry {log_id}")
    except SQLAlchemyError as e:
        payload.log_error(e)
        if self.request.retries < self.max_retries:
            payload.set_phase("lookup_log_registry_db_error", status="running")
        else:
            set_task_status(
                task_id=payload.task_id,
                status_dict={
                    "task_status": "failed",
                    "log_status": "not_found",
                    "log_id": log_id,
                },
            )
            payload.set_phase("lookup_log_registry_db_error", status="failed")

        logger.exception(f"[{payload.task_id}] Exception in {task_name}")
        raise
    finally:
        db.close()
        logger.debug(f"[{payload.task_id}] Database session closed in {task_name}.")

    return payload.model_dump()
