from celery import chain
from render_rig2.tasks_v2 import lookup_log_registry
from render_rig2.tasks_v2 import lookup_chart_registry
from render_rig2.tasks_v2 import get_existing_chart
from render_rig2.tasks_v2 import get_log_dispatch_chart
from render_rig2.tasks_v2 import log_chart_in_registry
from render_rig2.tasks_v2 import store_chart_json_in_s3

payload_dict = {"log_id": "1fc1b7b4-a68a-491b-8984-3234ed71be08", "chart_name": "chart_power"}

pipeline = chain(
    lookup_chart_registry.s(payload_dict),
    get_existing_chart.s(),
    lookup_log_registry.s(),
    get_log_dispatch_chart.s(),
    store_chart_json_in_s3.s(),
    log_chart_in_registry.s(),
    )

result = pipeline.apply_async()
# get the result
foo = result.get(timeout=60)

from pprint import pprint
pprint(foo)