from render_rig2.chart_engine import CHART_REGISTRY
from render_rig2.app import celery_app
from render_rig2.utils.logger import logger
from render_rig2.chart_engine.manager import generate_chart_for_log
from ypr_core_logfoundry.parser import ULogParser
from typing import Tuple


@celery_app.task(name="chart_dispatcher")
def chart_dispatcher(payload: Tuple[str, str, ULogParser]) -> str | None:
    # tuple structure is (log_id, chart_name, log_data)
    """
    Dispatches a chart rendering task to the appropriate chart engine.
    
    Args:
        payload (Tuple[str, str, ULogParser]): A tuple containing:
            - log_id (str): Identifier for the log.
            - chart_name (str): Name of the chart to render.
            - log_data (ULogParser): Parsed log data object.
    
    Returns:
        str | None: A JSON string representation of the rendered chart if successful, 
        otherwise None.
    """
    log_id, chart_name, log_data = payload
    if chart_name not in CHART_REGISTRY:
        logger.error(f"❌ Chart '{chart_name}' is not registered.")
        return None
    _chart = CHART_REGISTRY[chart_name]
    logger.info(f"🔧 Dispatching chart '{chart_name}' for log_id: {log_id}")
    chart_json = generate_chart_for_log(log_id, _chart, log_data)
    return chart_json