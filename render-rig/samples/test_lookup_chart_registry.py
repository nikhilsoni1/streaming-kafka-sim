from render_rig2.tasks import lookup_chart_registry
from render_rig2.logger import logger
from pprint import pprint

log_id = "1fc1b7b4-a68a-491b-8984-3234ed71be08"
chart_name = 'chart_accel_raw_xyz'



result = lookup_chart_registry(log_id, chart_name)
if result is not None:
    for item in result:
        pprint(item)
else:
    print(result)