from time import perf_counter
from render_rig2.utils.logger import logger


def generate_charts_for_log(log_data, chart) -> list:
    if chart.is_topic_available(log_data):
        t0_generate_chart = perf_counter()
        fig = chart.generate(log_data)
        t1_generate_chart = perf_counter()
        logger.info(
            f"✅ Generated {chart.chart_name} in {round(t1_generate_chart - t0_generate_chart, 2)}s"
        )
        chart_json = fig.to_json().encode("utf-8")
    return chart_json
