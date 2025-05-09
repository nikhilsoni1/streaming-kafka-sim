from render_rig2.tasks.store_chart_json_in_s3 import store_chart_json_in_s3
from render_rig2.tasks.log_chart_in_registry import log_chart_in_registry
import uuid
import datetime
import json
from pprint import pprint

log_id = f"{uuid.uuid4()}"
log_id = "025468ef-81b7-4ec6-87a4-19a323b77b17"
chart_name = f"del_this_{uuid.uuid4().hex}"
chart_json = {
    "log_id": log_id,
    "chart_name": chart_name,
    "log_ts_utc": datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S"
    ),
}
chart_json = json.dumps(chart_json)
result = store_chart_json_in_s3(
    log_id=log_id, chart_name=chart_name, chart_json=chart_json
)
pprint(result)
result2 = log_chart_in_registry(result)
print(result2)
