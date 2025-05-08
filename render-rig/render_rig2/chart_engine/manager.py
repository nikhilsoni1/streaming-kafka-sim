from typing import Optional
from render_rig2.utils.logger import logger
from render_rig2.chart_engine import Chart
from ypr_core_logfoundry.parser import ULogParser
from render_rig2.utils.cache import cache
from render_rig2.utils.timing import timed_debug_log


def generate_chart_for_log(
    log_id: str, chart: Chart, log_data: ULogParser
) -> Optional[bytes]:
    """
    Generates a chart for a given log ID using the specified chart engine.
    Args:
        log_id (str): The unique identifier for the log.
        chart (Chart): The chart engine to use for rendering.
        log_data (ULogParser): The parsed log data object.
    Returns:
        Optional[bytes]: A JSON string representation of the rendered chart if successful,
        otherwise None.
    Todo:
        - Remove caching in the future as it is redundant.
    """
    chart_name = chart.chart_name
    cache_key = f"{log_id}::{chart_name}"

    # Try cache first
    with timed_debug_log(
        f"Cache lookup for log_id: {log_id}, chart_name: {chart_name}"
    ):
        cached = cache.get(cache_key, default=None, read=True)
    if cached is not None:
        logger.success(f"Cache hit for log_id: {log_id}, chart_name: {chart_name}")
        return cached

    # Instantiate chart engine
    chart_instance = chart()

    if not chart_instance.is_topic_available(log_data=log_data):
        return None

    # Generate chart
    with timed_debug_log(
        f"Generating chart for log_id: {log_id}, chart_name: {chart_name}"
    ):
        fig = chart_instance.generate(log_data)
    chart_json = fig.to_json()
    logger.success(f"Chart generated for log_id: {log_id}, chart_name: {chart_name}")

    # Store in cache (no lock)
    cache.set(cache_key, chart_json)

    return chart_json
