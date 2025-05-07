from render_rig2.tasks.get_existing_log import get_existing_log
from render_rig2.tasks.chart_dispatcher import chart_dispatcher
from pprint import pprint
payload = ('flight-px4-logs', 'raw-logs/2025/4/8/file_64c166b0dd104e44bd81adb9bddfb5bb.ulg')
log_data = get_existing_log(payload)
chart_name = "chart_accel_raw_xyz"
chart_json = chart_dispatcher(log_data, chart_name)
# print descriptive info about chart_json, size in MB, hash
chart_json_size = len(chart_json) / (1024 * 1024)  # Convert to MB
chart_json_hash = hash(chart_json)
print(f"Chart JSON size: {chart_json_size:.2f} MB")
print(f"Chart JSON hash: {chart_json_hash}")
