# render_accel_chart.py
from render_rig2.tasks.get_log_dispatch_chart import get_existing_log
from render_rig2.tasks.lookup_log_registry import lookup_log_registry
from render_rig2.chart_engine.charts import ChartAccelRawXYZ


log_id = "1fc1b7b4-a68a-491b-8984-3234ed71be08"
payload = lookup_log_registry(log_id)
_log_id, bucket_name, key = payload
assert _log_id == log_id, f"Log ID mismatch: {log_id} != {_log_id}"
result = get_existing_log(bucket_name, key)
print(result)



# Generate the chart
chart = ChartAccelRawXYZ()
if chart.is_topic_available(result):
    fig = chart.generate(result)
    fig.show()  # Opens in browser or notebook
else:
    print("sensor_combined topic not found in this log.")
