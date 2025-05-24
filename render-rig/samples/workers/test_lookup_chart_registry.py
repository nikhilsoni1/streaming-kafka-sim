from render_rig2.tasks.lookup_chart_registry import lookup_chart_registry
from render_rig2.tasks import get_existing_chart
from celery import chain

log_id = "1fc1b7b4-a68a-491b-8984-3234ed71be08"
chart_name = "chart_accel_raw_xyz"

pipeline1 = chain(
    lookup_chart_registry.s(log_id, chart_name),
    get_existing_chart.s(),
)
_task = pipeline1.apply_async()
_result = _task.get(timeout=60)
# print size of result1 in MB
print(f"Result Size: {(len(_result) / (1024 * 1024)):.1f} MB")
