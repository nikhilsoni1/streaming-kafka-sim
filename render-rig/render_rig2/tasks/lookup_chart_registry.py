from render_rig2.app import celery_app
from render_rig2.utils.logger import logger
from render_rig2.database_access.sessions.render_rig_session_local import (
    RenderRigSessionLocal,
)
from render_rig2.database_access.models.render_rig_registry_model import ChartRegistry
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Tuple
from render_rig2.utils.timing import timed_debug_log


@celery_app.task(name="lookup_chart_registry")
def lookup_chart_registry(
    log_id: str, chart_name: str
) -> Optional[Tuple[str, str, str]]:
    """
    Lookup the chart registry for a given log_id and chart_name.
    This function queries the ChartRegistry table to find the bucket name and key
    associated with the provided log_id and chart_name.
    If the record exists, it returns a tuple of (bucket_name, key).
    If the record does not exist, it returns None.

    Args:
        log_id (str): The log ID to look up.
        chart_name (str): The name of the chart to look up.

    Returns:
        Optional[Tuple[str, str, str]]: (log_id, bucket_name, key) if the record exists, else None.
    """

    db = RenderRigSessionLocal()
    try:
        with timed_debug_log(f"lookup_chart_registry for {log_id} - {chart_name}"):
            result = (
                db.query(
                    ChartRegistry.bucket_name,
                    ChartRegistry.key,
                )
                .filter_by(log_id=log_id, chart_name=chart_name)
                .first()
            )
        if result:
            logger.success(f"Found chart registry entry for {log_id} - {chart_name}")
            bucket_name, key = result
            result = (log_id, bucket_name, key)
            return result
        logger.success(f"Lookup ok but no entry found for {log_id} - {chart_name}")
        return None
    except SQLAlchemyError as e:
        logger.exception(f"Database error while querying ChartRegistry: {e}")
        raise RuntimeError(f"Database error while querying ChartRegistry: {e}")
