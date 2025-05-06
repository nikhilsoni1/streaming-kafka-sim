from render_rig2.tasks.get_existing_log import get_existing_log
payload = ('flight-px4-logs', 'raw-logs/2025/4/8/file_64c166b0dd104e44bd81adb9bddfb5bb.ulg')
result = get_existing_log(payload)
print(result)