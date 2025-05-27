from sqlalchemy.exc import SQLAlchemyError
from render_rig2.app_v2 import celery_app
from render_rig2.contracts import TaskPayload
from render_rig2.database_access.models.render_rig_registry_model import ChartRegistry
from render_rig2.database_access.sessions.render_rig_session_local import (
    RenderRigSessionLocal,
)
from render_rig2.utils.logger import logger


@celery_app.task(
    name="lookup_chart_registry",
    bind=True,
    autoretry_for=(SQLAlchemyError,),
    retry_backoff=True,
    max_retries=3,
)
def lookup_chart_registry(self, payload_dict: dict) -> dict:
    """
    Looks up the chart in the ChartRegistry by log_id and chart_name.

    Args:
        payload_dict (dict): Serialized ChartTaskPayload dictionary.

    Returns:
        dict: A dictionary representation of ChartTaskPayload, including phase/status/result updates.
              If a registry entry is found, result includes S3 reference info.
              If not found, result is None and status is set to 'need_generation'.
              On DB error, status is 'failed' and errors are logged.
    """

    # Validate and deserialize the payload dictionary
    payload = TaskPayload.model_validate(payload_dict)

    # Set the initial phase and log the start of the task
    task_name = self.name
    payload.set_phase(
        phase="init_lookup_chart_registry", task_name=task_name, status="running"
    )
    log_id = payload.log_id
    chart_name = payload.chart_name
    logger.info(
        f"[{payload.task_id}] {task_name} started for log_id={payload.log_id}, chart_name={payload.chart_name}"
    )

    # Initialize the database session
    db = RenderRigSessionLocal()
    try:
        result = (
            db.query(
                ChartRegistry.bucket_name,
                ChartRegistry.key,
            )
            .filter_by(log_id=log_id, chart_name=chart_name)
            .first()
        )
        if result:
            # If a chart is found in the registry, set the result with S3 reference info
            bucket_name, key = result
            payload.set_result(
                source="chart_registry",
                type_="reference",
                data={
                    "log_id": payload.log_id,
                    "bucket_name": bucket_name,
                    "key": key,
                },
            )
            payload.set_phase(phase="chart_found_in_registry", status="running")
        else:
            payload.result = None
            payload.set_phase(phase="no_chart_found_in_registry", status="running")

    except SQLAlchemyError as e:
        payload.log_error(e)
        if self.request.retries < self.max_retries:
            payload.set_phase(
                phase="lookup_chart_registry_db_error_retry", status="running"
            )
        else:
            payload.set_phase(phase="lookup_chart_registry_db_error", status="running")
        logger.exception(
            f"[{payload.task_id}] SQLAlchemyError Exception in {task_name}"
        )
        raise
    finally:
        db.close()
        logger.debug(f"[{payload.task_id}] Database session closed in {task_name}.")

    return payload.model_dump()
