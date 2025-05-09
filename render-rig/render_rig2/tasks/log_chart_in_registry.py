from render_rig2.app import celery_app
from render_rig2.utils.logger import logger
from render_rig2.database_access.sessions.render_rig_session_local import (
    RenderRigSessionLocal,
)
from render_rig2.database_access.models.render_rig_registry_model import ChartRegistry
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Tuple
from render_rig2.utils.timing import timed_debug_log


@celery_app.task(name="log_chart_in_registry")
def log_chart_in_registry(payload: dict) -> Optional[bool]:
    """
    Logs chart metadata into the registry database.

    Args:
        payload (dict): A dictionary containing the following chart metadata:
            - log_id (str): Unique identifier for the log entry.
            - chart_name (str): Name of the chart.
            - chart_id (str): Unique identifier for the chart.
            - chart_hash_sha256 (str): SHA-256 hash of the chart file.
            - bucket_name (str): Name of the S3 bucket where the chart is stored.
            - key (str): S3 key corresponding to the chart file.
            - log_ts_utc (str): UTC timestamp of when the log entry was created.
            - upd_ts_utc (str): UTC timestamp of the last update to the log entry.

    Returns:
        Optional[bool]: 
            - True if the chart metadata was successfully logged.
            - False if there was a database error during the operation.
            - None if the provided payload is invalid (e.g., None).
    """
    if payload is None:
        logger.error("Payload is None, cannot log chart in registry.")
        return None

    try:
        record = ChartRegistry(**payload)
    except TypeError as e:
        logger.error(f"Error creating ChartRegistry object: {e}")
        return None
    
    try:
        with timed_debug_log(f"Logging chart metadata for {record.log_id} - {record.chart_name}"):
            db = RenderRigSessionLocal()
            db.add(record)
            db.commit()
        logger.success(f"Chart metadata logged successfully for {record.log_id} - {record.chart_name}")
        return True
    except SQLAlchemyError as e:
        logger.exception(f"Database error while logging chart metadata: {e}")
        db.rollback()
        return False
    finally:
        db.close()
    