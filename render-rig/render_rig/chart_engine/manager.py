# manager.py

from render_rig.chart_engine.charts.chart_acceleration_raw_xyz import ChartAccelRawXYZ
from render_rig.logfoundry_bridge.parser_adapter import get_log_data
from render_rig.cache.store import save_chart_json
from render_rig.cache.store import chart_exists

ALL_CHARTS = [ChartAccelRawXYZ()]


def generate_charts_for_log(log_id: str) -> list:
    log_data = get_log_data(log_id)
    results = []

    for chart in ALL_CHARTS:
        chart_id = f"{log_id}_{chart.chart_name}"
        # Check if (log_id, chart.chart_name) exists in registry
        # fetch chart_json if exists -> continue
        # else generate chart and save to registry
        if chart_exists(chart_id):
            results.append({"chart_id": chart_id, "status": "cached"})
            continue
        # Check if topic is available in the dataset
        if chart.is_topic_available(log_data):
            fig = chart.generate(log_data)
            save_chart_json(fig, chart_id)
            results.append({"chart_id": chart_id, "status": "generated"})
        else:
            # log
            pass

    return results
