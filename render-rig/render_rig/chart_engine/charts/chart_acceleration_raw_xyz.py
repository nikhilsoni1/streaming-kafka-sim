# chart_accel_raw_xyz.py

from render_rig.chart_engine.base import Chart
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class ChartAccelRawXYZ(Chart):
    chart_name = "chart_accel_raw_xyz"

    def is_available(self, log_data: dict) -> bool:
        return "sensor_combined" in log_data

    def generate(self, log_data: dict):
        df = log_data["sensor_combined"]

        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            subplot_titles=("Accel X", "Accel Y", "Accel Z"),
                            vertical_spacing=0.05)

        fig.add_trace(go.Scatter(x=df["timestamp"], y=df["accelerometer_m_s2[0]"],
                                 mode="lines", name="Accel X"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["timestamp"], y=df["accelerometer_m_s2[1]"],
                                 mode="lines", name="Accel Y"), row=2, col=1)
        fig.add_trace(go.Scatter(x=df["timestamp"], y=df["accelerometer_m_s2[2]"],
                                 mode="lines", name="Accel Z"), row=3, col=1)

        fig.update_layout(title_text="Raw Acceleration", height=600, showlegend=False)
        return fig
