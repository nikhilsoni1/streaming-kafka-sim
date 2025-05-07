from time import perf_counter
from render_rig2.utils.logger import logger
from render_rig2.chart_engine import Chart
from ypr_core_logfoundry.parser import ULogParser

def generate_chart_for_log(log_data: ULogParser, chart: Chart) -> list:
    chart_engine = chart()
    chart_json = None
    print(chart_engine.chart_name)
    if chart_engine.is_topic_available(log_data=log_data):
        t0_generate_chart = perf_counter()
        fig = chart_engine.generate(log_data)
        t1_generate_chart = perf_counter()
        time_to_generate_chart = t1_generate_chart - t0_generate_chart
        logger.info(
            f"✅ Generated {chart_engine.chart_name} in {round(time_to_generate_chart, 2)}s"
        )
        chart_json = fig.to_json().encode("utf-8")
    return chart_json
