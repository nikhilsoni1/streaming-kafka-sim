# render_accel_chart.py

from render_rig import get_log_data
from render_rig import ChartAccelRawXYZ
from render_rig.utils import hash_bytes_sha256

# Load and parse the .ulg file
log_data = get_log_data("1fc1b7b4-a68a-491b-8984-3234ed71be08")

# Generate the chart
chart = ChartAccelRawXYZ()
if chart.is_topic_available(log_data):
    fig = chart.generate(log_data)
    fig_json = fig.to_json().encode("utf-8")
    fig_hash_sha256 = hash_bytes_sha256(fig_json)
    print(f"Chart hash: {fig_hash_sha256}")
    fig.show()  # Opens in browser or notebook
else:
    print("sensor_combined topic not found in this log.")
