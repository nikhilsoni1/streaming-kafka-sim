# chart_power.py

from render_rig2.chart_engine.base import Chart
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from render_rig2.utils.logger import logger


class ChartPower(Chart):
    chart_name = "chart_power"
    topic_name = "battery_status"

    def is_topic_available(self, log_data: dict) -> bool:
        if self.topic_name in log_data.list_topics():
            return True
        return False

    def generate(self, log_data: dict):
        df = log_data.get_topic_df(self.topic_name)

        is_ocv_estimate_available = "ocv_estimate" in df.columns
        is_internal_resistance_estimate_available = "internal_resistance_estimate" in df.columns
        include_third_row = is_ocv_estimate_available and is_internal_resistance_estimate_available

        rows = 3 if include_third_row else 2
        subplot_titles = ["Voltage & Current", "Battery Status"]
        if include_third_row:
            subplot_titles.append("Internal Estimates")

        fig = make_subplots(
            rows=rows,
            cols=1,
            shared_xaxes=True,
            subplot_titles=tuple(subplot_titles),
            vertical_spacing=0.05,
        )

        # First subplot: Voltage and Current
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"].tolist(),
                y=df["voltage_v"].tolist(),
                mode="lines",
                name="Battery Voltage [V]",
            ), row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"].tolist(),
                y=df["current_a"].tolist(),
                mode="lines",
                name="Battery Current [A]",
            ), row=1, col=1
        )

        # Second subplot: Battery discharged and remaining
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"].tolist(),
                y=df["discharged_mah"].divide(100).round(2).tolist(),
                mode="lines",
                name="Discharged Amount [mAh / 100]",
            ), row=2, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"].tolist(),
                y=df["remaining"].multiply(100).round(2).tolist(),
                mode="lines",
                name="Battery remaining [0=empty, 10=full]",
            ), row=2, col=1
        )

        # Optional third subplot
        if include_third_row:
            fig.add_trace(
                go.Scatter(
                    x=df["timestamp"].tolist(),
                    y=df["ocv_estimate"].tolist(),
                    mode="lines",
                    name="OCV Estimate [V]",
                ), row=3, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=df["timestamp"].tolist(),
                    y=df["internal_resistance_estimate"].multiply(1000).round(2).tolist(),
                    mode="lines",
                    name="Internal Resistance Estimate [mOhm]",
                ), row=3, col=1
            )
        else:
            logger.info(
                f"OCV estimate, available: {is_ocv_estimate_available} or Internal resistance estimate, available: {is_internal_resistance_estimate_available}."
            )

        fig.update_layout(
            title_text="Power",
            height=700,
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        )

        return fig
