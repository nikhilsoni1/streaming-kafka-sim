from render_rig2.tasks.get_existing_log import get_existing_log
from render_rig2.tasks.lookup_log_registry import lookup_log_registry

log_id = "1fc1b7b4-a68a-491b-8984-3234ed71be08"
payload = lookup_log_registry(log_id)
result = get_existing_log(payload)
print(result)