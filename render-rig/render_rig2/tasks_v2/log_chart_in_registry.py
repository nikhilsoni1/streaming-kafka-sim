from render_rig2.app import celery_app
from render_rig2.utils.logger import logger
from render_rig2.database_access.sessions.render_rig_session_local import (
    RenderRigSessionLocal,
)
from render_rig2.database_access.models.render_rig_registry_model import ChartRegistry
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
from render_rig2.contracts import TaskPayload


@celery_app.task(name="log_chart_in_registry", bind=True)
def log_chart_in_registry(self, payload_dict: dict) -> dict:
    """
    Logs chart metadata into the registry database.

    Args:
        payload_dict (dict): Serialized TaskPayload containing chart metadata in result.

    Returns:
        dict: Updated TaskPayload with status and error logs.
    """
    payload = TaskPayload.model_validate(payload_dict)
    task_name = self.name
    payload.retries = self.request.retries
    payload.set_phase("init_log_chart_in_registry", task_name=task_name, status="running")

    # Stop early if meta indicates so
    if payload.meta.get("stop_chain") is True:
        payload.set_phase("skipped_due_to_meta_flag", status="skipped")
        logger.info(f"[{payload.task_id}] {task_name} skipped due to meta['stop_chain']=True")
        return payload.model_dump()

    try:
        # Validate the result source/type
        payload.require_result_type("reference", expected_source="s3")

        metadata = {
            "log_id": payload.log_id,
            "chart_name": payload.chart_name,
            "bucket_name": payload.result.data.get("bucket_name"),
            "key": payload.result.data.get("key"),
            "chart_id": str(uuid.uuid4()),
            "chart_hash_sha256": payload.meta.get("chart_hash_sha256"),
            "log_ts_utc": payload.meta.get("log_ts_utc", datetime.utcnow().isoformat()),
            "upd_ts_utc": datetime.utcnow().isoformat(),
        }

        # Create DB record
        try:
            record = ChartRegistry(**metadata)
        except TypeError as e:
            payload.log_error(f"Invalid metadata for ChartRegistry: {e}")
            payload.set_phase("chart_registry_build_failed", status="failed")
            logger.error(f"[{payload.task_id}] Metadata construction failed: {e}")
            return payload.model_dump()

        # Commit to DB
        db = RenderRigSessionLocal()
        db.add(record)
        db.commit()
        payload.set_phase("chart_registry_entry_created", status="success")
        logger.info(f"[{payload.task_id}] Chart metadata logged for {metadata['log_id']} - {metadata['chart_name']}")

    except SQLAlchemyError as e:
        db.rollback()
        payload.log_error(e)
        payload.set_phase("db_commit_failed", status="failed")
        logger.exception(f"[{payload.task_id}] Database error while logging chart metadata")

    except Exception as e:
        payload.log_error(e)
        payload.set_phase("log_chart_registry_failed", status="failed")
        logger.exception(f"[{payload.task_id}] Unexpected error in {task_name}")

    finally:
        db.close()

    return payload.model_dump()

