from render_rig2.tasks.get_existing_chart import get_existing_chart

payload = ('flight-render-rig', 'charts/1fc1b7b4-a68a-491b-8984-3234ed71be08/chart_accel_raw_xyz/45b26608d98246d69c58828d116bd6b8.json')

result = get_existing_chart(payload)
print(result)