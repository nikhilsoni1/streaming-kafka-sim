# chart_power.py

from render_rig2.chart_engine.base import Chart
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from render_rig2.utils.logger import logger
import pandas as pd


class ChartVibrationMetrics(Chart):
    chart_name = "chart_vibration_metrics"
    topic_name = "vehicle_imu_status"

    def is_topic_available(self, log_data: dict) -> bool:
        if self.topic_name in log_data.list_topics():
            return True
        return False

    def generate(self, log_data: dict):

        multi_id = len(log_data.topic_map.get(self.topic_name))
        fig = make_subplots(
            rows=1,
            cols=1
        )
        for i in range(multi_id):
            df = log_data.get_topic_df(self.topic_name, index=i)
            _name = f"Accel {i} Vibration Level [m/s^2]"
            fig.add_trace(
                go.Scatter(
                    x=df["timestamp"].tolist(),
                    y=df["accel_vibration_metric"].tolist(),
                    mode="lines",
                    name=_name,
                ), row=1, col=1
            )

        fig.update_layout(
            title_text="Vibration Metrics",
            height=700,
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            xaxis_title="Timestamp",
            yaxis_title="Vibration Level [m/s^2]"
        )
        return fig
