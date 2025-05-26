from diskcache import Cache
from render_rig2.tasks.get_log_dispatch_chart import get_existing_log
from render_rig2.tasks.lookup_log_registry import lookup_log_registry
from render_rig2.chart_engine.charts import ChartPower

# Setup cache
cache = Cache("/tmp/render_cache")

log_id = "1fc1b7b4-a68a-491b-8984-3234ed71be08"
log_id = "7b74d038-ea95-4cd4-82a9-919d1155a6a3"

# Cache lookup_log_registry
if log_id in cache:
    payload = cache[log_id]
    print("Used cache for log registry lookup.")
else:
    payload = lookup_log_registry(log_id)
    cache[log_id] = payload
    print("Cached result of log registry lookup.")

_log_id, bucket_name, key = payload
assert _log_id == log_id, f"Log ID mismatch: {log_id} != {_log_id}"

# Cache get_existing_log using composite key
log_cache_key = f"{bucket_name}:{key}"
if log_cache_key in cache:
    result = cache[log_cache_key]
    print(f"Used cache for get_existing_log. {result}")
else:
    result = get_existing_log(bucket_name, key)
    cache[log_cache_key] = result
    print(f"Cached result of get_existing_log.")

# Generate the chart
chart = ChartPower()
if chart.is_topic_available(result):
    print("topic available")
    fig = chart.generate(result)
    fig.show()
else:
    print("sensor_combined topic not found in this log.")
