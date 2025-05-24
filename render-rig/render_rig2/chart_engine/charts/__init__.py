from .chart_acceleration_raw_xyz import ChartAccelRawXYZ
from .chart_power import ChartPower
from .chart_vibration_metrics import ChartVibrationMetrics

CHART_REGISTRY = {
    "chart_accel_raw_xyz": ChartAccelRawXYZ,
    "chart_power": ChartPower,
    "chart_vibration_metrics": ChartVibrationMetrics,
}
