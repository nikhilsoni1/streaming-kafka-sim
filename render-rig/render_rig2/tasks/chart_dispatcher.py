from render_rig2.chart_engine import CHART_REGISTRY
# import os
# import tempfile
from time import perf_counter
# from botocore.exceptions import ClientError

from render_rig2.app import celery_app
from render_rig2.utils.logger import logger
# from render_rig2.object_access.client import create_boto3_client
from render_rig2.utils.cache import cache
from render_rig2.chart_engine.manager import generate_chart_for_log
# from ypr_core_logfoundry.parser import ULogParser


@celery_app.task(name="chart_dispatcher")
def chart_dispatcher(log_data, chart_name):
    """
    Dispatches a chart to the appropriate chart engine for rendering.
    Args:
        log_data (dict): The log data to be rendered.
        chart (str): The name of the chart to be rendered.
    Returns:
        dict: The rendered chart data.
    """
    # Check if the chart is registered
    if chart_name not in CHART_REGISTRY:
        logger.error(f"❌ Chart '{chart_name}' is not registered.")
        return None
    chart = CHART_REGISTRY[chart_name]
    chart_json = generate_chart_for_log(log_data, chart)
    return chart_json