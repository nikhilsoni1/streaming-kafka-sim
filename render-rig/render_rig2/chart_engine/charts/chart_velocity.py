# chart_power.py

from render_rig2.chart_engine.base import Chart
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from render_rig2.utils.logger import logger
import pandas as pd


class ChartVelocity(Chart):
    chart_name = "chart_velocity"
    topic_name = "vehicle_local_position"

    def is_topic_available(self, log_data: dict) -> bool:
        if self.topic_name in log_data.list_topics():
            return True
        return False

    def generate(self, log_data: dict):
        df1 = log_data.get_topic_df(self.topic_name, index=0)
        df2 = log_data.get_topic_df("vehicle_local_position_setpoint", index=0)
        fig = make_subplots(
            rows=1,
            cols=1
        )

        # velocity
        fig.add_trace(
            go.Scatter(
                x=df1["timestamp"].tolist(),
                y=df1["vx"].tolist(),
                mode="lines",
                name="X",
            ), row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df1["timestamp"].tolist(),
                y=df1["vy"].tolist(),
                mode="lines",
                name="Y",
            ), row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df1["timestamp"].tolist(),
                y=df1["vz"].tolist(),
                mode="lines",
                name="Z",
            ), row=1, col=1
        )

        # velocity setpoint
        fig.add_trace(
            go.Scatter(
                x=df2["timestamp"].tolist(),
                y=df2["vx"].tolist(),
                mode="lines",
                name="X Setpoint",
                line=dict(dash='dash')
            ), row=1, col=1
        )

        fig.add_trace(
            go.Scatter(
                x=df2["timestamp"].tolist(),
                y=df2["vy"].tolist(),
                mode="lines",
                name="Y Setpoint",
                line=dict(dash='dash')
            ), row=1, col=1
        )

        fig.add_trace(
            go.Scatter(
                x=df2["timestamp"].tolist(),
                y=df2["vz"].tolist(),
                mode="lines",
                name="Z Setpoint",
                line=dict(dash='dash')
            ), row=1, col=1
        )

        fig.update_layout(
            title_text="Velocity",
            height=700,
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            xaxis_title="Timestamp",
            yaxis_title="Velocity [m/s]"
        )
        return fig
