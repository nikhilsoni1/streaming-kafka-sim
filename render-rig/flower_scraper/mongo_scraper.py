from pymongo import MongoClient
import re
import pandas as pd
import json
import ast
import re
import datetime
from pprint import pprint

# Initialize MongoDB client

client = MongoClient("mongodb://localhost:27017")
db = client["render-rig2-tasks"]
collection = db["group1"]

# Define the regex pattern
pattern = re.compile("bcb96996-b312-4b7d-baed-4eeef8acc83c")

# Build and execute the query
query = {
    "value.result": {"$regex": pattern}
}

# Fetch documents
results = collection.find(query)

keep = ["uuid", "name", "state", "received", "started", "succeeded", "result"]

filtered_store = list()
# Print the results
for doc in results:
    id = doc["_id"]
    for k, v in doc["value"].items():
        if k == "result":
            try:
                parsed_result = ast.literal_eval(v)
                doc["value"][k] = parsed_result
                flag = True
                with open("result.json", "w") as f:
                    json.dump(doc, f, indent=4)
            except (ValueError, SyntaxError) as e:
                print("Could not parse result:", e)
    
    filtered_doc = {k: v for k, v in doc["value"].items() if k in keep}
    filtered_store.append(filtered_doc)
    # for k in doc["value"].keys():
    #     print(k)
    # break

def filter_payload(payload):
    keep_keys = ["chart_name", "log_id", "phase", "status", "task_id", "task_name"]
    return {k: v for k, v in payload.items() if k in keep_keys}

# write a function that return a dictionary with prefixed keys
def prefix_keys(payload, prefix):
    return {f"{prefix}_{k}": v for k, v in payload.items()}

_store = list()
for i in filtered_store:
    payload = i.pop("result")
    try:
        errors = payload.pop("errors", None)
    except AttributeError:
        pass
    meta = payload.pop("meta", None)
    if meta:
        pprint(meta)
    a = prefix_keys(i.copy(), "flower")
    celery_result = payload.pop("result")
    if celery_result is not None:
        celery_result.pop("data")
        celery_result = prefix_keys(celery_result.copy(), "result")
    else:
        celery_result = {}
    p2 = filter_payload(payload)
    if errors:
        p2["errors"] = "; ".join(errors)
    p2 = prefix_keys(p2.copy(), "worker")
    p2.update(celery_result)
    # print("-" * 20)
    final = {**a, **p2}
    _store.append(final)
    # break
df = pd.DataFrame(_store)

df["flower_received"] = pd.to_datetime(df["flower_received"], unit='s')
df["flower_started"] = pd.to_datetime(df["flower_started"], unit='s')
df["flower_succeeded"] = pd.to_datetime(df["flower_succeeded"], unit='s')

df = df.sort_values(by=["worker_log_id", "worker_chart_name", "flower_received"])
df.to_csv("flower_scraper.csv", index=False)

final_keep = ["flower_uuid", "flower_received", "worker_log_id", "worker_chart_name", "worker_task_name", "worker_status", "worker_phase", "result_source", "result_type", "worker_errors"]
df = df[final_keep]
df.to_csv("flower_scraper_final.csv", index=False)
client.close()

x = "{'task_id': 'e957410117694433b1c09edf35db9e06', 'task_name': 'get_log_dispatch_chart', 'log_id': 'bcb96996-b312-4b7d-baed-4eeef8acc83c', 'chart_name': 'chart_velocity', 'webhook_url': None, 'status': 'failed', 'phase': 'chart_dispatch_error', 'retries': 0, 'errors': ['3 validation errors for ResultPayload\ndata.dict[any,any]\n  Input should be a valid dictionary [type=dict_type, input_value=None, input_type=NoneType]\n    For further information visit https://errors.pydantic.dev/2.11/v/dict_type\ndata.str\n  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]\n    For further information visit https://errors.pydantic.dev/2.11/v/string_type\ndata.bytes\n  Input should be a valid bytes [type=bytes_type, input_value=None, input_type=NoneType]\n    For further information visit https://errors.pydantic.dev/2.11/v/bytes_type'], 'logs': [], 'result': {'source': 'log_registry', 'type': 'raw_log', 'data': {'log_id': 'bcb96996-b312-4b7d-baed-4eeef8acc83c', 'bucket_name': 'flight-px4-logs', 'k...', ...}}}"