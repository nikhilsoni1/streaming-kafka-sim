from render_rig2.tasks.get_existing_log import get_existing_log
from render_rig2.tasks.chart_dispatcher import chart_dispatcher
from render_rig2.tasks.lookup_log_registry import lookup_log_registry
import hashlib

log_id = "1fc1b7b4-a68a-491b-8984-3234ed71be08"
payload1 = lookup_log_registry(log_id)
payload2 = get_existing_log(payload1)
log_id, log_data = payload2
chart_name = "chart_accel_raw_xyz"
payload3 = (log_id, chart_name, log_data)
chart_json = chart_dispatcher(payload3)
chart_json_size = len(chart_json) / (1024 * 1024)
# calculate sha256 hash of chart_json
hash_object = hashlib.sha256(chart_json)
hash_hex = hash_object.hexdigest()
print(f"Chart JSON size: {chart_json_size:.2f} MB")
print(f"Chart JSON hash: {hash_hex}")
