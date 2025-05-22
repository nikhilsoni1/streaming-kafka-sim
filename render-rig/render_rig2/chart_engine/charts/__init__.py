from .chart_acceleration_raw_xyz import ChartAccelRawXYZ
from .chart_power import ChartPower

CHART_REGISTRY = {
    "chart_accel_raw_xyz": ChartAccelRawXYZ,
    "chart_power": ChartPower,
}
