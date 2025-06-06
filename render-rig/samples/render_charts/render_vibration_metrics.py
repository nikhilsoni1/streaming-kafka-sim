from diskcache import Cache
from render_rig2.tasks.get_log_dispatch_chart import get_existing_log
from render_rig2.tasks.lookup_log_registry import lookup_log_registry
from render_rig2.chart_engine.charts import ChartVibrationMetrics

# Setup cache
cache = Cache("/tmp/render_cache")

log_id = "1fc1b7b4-a68a-491b-8984-3234ed71be08"

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
chart = ChartVibrationMetrics()
multi_id = len(result.topic_map.get(chart.topic_name))
if chart.is_topic_available(result):
    print(f"Topic: {chart.topic_name} found in this log.")
    fig = chart.generate(result)
    fig.show()
else:
    print(f"Topic: {chart.topic_name} not found in this log.")
