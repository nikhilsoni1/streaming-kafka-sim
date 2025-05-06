from render_rig2.app import celery_app
from render_rig2.logger import logger
from render_rig2.database_access.sessions.render_rig_session_local import (
    RenderRigSessionLocal,
)
from render_rig2.database_access.models.render_rig_registry_model import ChartRegistry
from time import perf_counter
from sqlalchemy.exc import SQLAlchemyError


@celery_app.task(name="lookup_chart_registry")
def lookup_chart_registry(log_id, chart_name):
    """
    Looks up the ChartRegistry entry for a given log_id and chart_name.
    Returns:
        Optional[Tuple[str, str]]: (bucket_name, key) if the record exists, else None.
    """
    db = RenderRigSessionLocal()
    try:
        t0 = perf_counter()
        result = (
            db.query(
                ChartRegistry.bucket_name,
                ChartRegistry.key,
            )
            .filter_by(log_id=log_id, chart_name=chart_name)
            .first()
        )
        t1 = perf_counter()
        el1 = t1 - t0
        logger.info(
            f"lookup_chart_registry took {el1:.4f} seconds for log_id: {log_id}"
        )
        if result:
            return result
        return None
    except SQLAlchemyError as e:
        logger.exception(f"Database error while querying ChartRegistry: {e}")
        raise RuntimeError(f"Database error while querying ChartRegistry: {e}")
