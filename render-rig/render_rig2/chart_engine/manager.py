from time import perf_counter
from typing import Optional
from render_rig2.utils.logger import logger
from render_rig2.chart_engine import Chart
from ypr_core_logfoundry.parser import ULogParser
from render_rig2.utils.cache import cache

def generate_chart_for_log(log_id: str, chart: Chart, log_data: ULogParser) -> Optional[bytes]:
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
    t0_get_cache = perf_counter()
    cached = cache.get(cache_key, default=None, read=True)
    t1_get_cache = perf_counter()
    time_to_get_cache = round(t1_get_cache - t0_get_cache, 2)
    if cached is not None and 1==2:
        read_cached = cached.read()
        logger.info(f"🧠 Cache hit for log_id: {log_id}, chart_name: {chart_name}, duration: {time_to_get_cache}")
        return read_cached

    # Instantiate chart engine
    chart_instance = chart()

    if not chart_instance.is_topic_available(log_data=log_data):
        return None

    # Generate chart
    start_time = perf_counter()
    fig = chart_instance.generate(log_data)
    # show(fig)
    # save fig as png
    fname = f"/Users/nikhilsoni/Downloads/{log_id}_{chart_name}.png"
    fig.write_image(fname, format="png", scale=2, width=800, height=600)
    end_time = perf_counter()

    duration = round(end_time - start_time, 2)
    chart_json = fig.to_json()
    fname = f"/Users/nikhilsoni/Downloads/{log_id}_{chart_name}.json"
    import json
    x1 = fig.to_plotly_json()
    with open(fname, "w") as f:
        json.dump(x1, f, indent=4)

    logger.info(
        f"✅ Chart generated for log_id: {log_id}, chart_name: {chart_name} in {duration}s"
    )

    # Store in cache (no lock)
    cache.set(cache_key, chart_json)

    return chart_json
