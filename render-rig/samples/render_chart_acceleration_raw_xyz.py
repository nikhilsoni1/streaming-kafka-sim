# render_accel_chart.py

from render_rig import get_log_data
from render_rig import ChartAccelRawXYZ

# Load and parse the .ulg file
log_data = get_log_data("52dac5ff-484c-4737-9ee5-03aa07a5b051")

# Generate the chart
chart = ChartAccelRawXYZ()
if chart.is_available(log_data):
    fig = chart.generate(log_data)
    fig.show()  # Opens in browser or notebook
else:
    print("sensor_combined topic not found in this log.")
