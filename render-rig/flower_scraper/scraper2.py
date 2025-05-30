import argparse
import json
import re
import hashlib
from pprint import pprint

import requests
import pandas as pd
from tqdm import tqdm
from pymongo import MongoClient
from celery import Celery
from celery.result import AsyncResult
from sqlalchemy import create_engine

# -----------------------------
# Configuration
# -----------------------------
MONGO_URI = "mongodb://localhost:27017"
MONGO_DB = "render-rig2-tasks"
MONGO_COLLECTION = "group1"

REDIS_BROKER = "redis://localhost:6379/0"
REDIS_BACKEND = "redis://localhost:6379/1"

POSTGRES_URI = "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"
POSTGRES_TABLE = "control"

FLOWER_TASK_API = "http://localhost:5555/api/tasks"

# -----------------------------
# Utilities
# -----------------------------
def prefix_keys(payload, prefix):
    return {f"{prefix}_{k}": v for k, v in payload.items()}

def clean_list(lst):
    return "; ".join(str(item).strip().replace("\n", " ") for item in lst if item).strip()

def sha256_of_dataframe(df: pd.DataFrame) -> str:
    df_sorted = df.sort_index(axis=1).sort_values(by=df.columns.tolist()).reset_index(drop=True)
    csv_bytes = df_sorted.to_csv(index=False).encode("utf-8")
    return hashlib.sha256(csv_bytes).hexdigest()

# -----------------------------
# CLI Argument
# -----------------------------
parser = argparse.ArgumentParser(description="Fetch and store Celery task results by task ID pattern.")
parser.add_argument("task_id_pattern", type=str, help="Regex pattern to match task_id in result")
args = parser.parse_args()
pattern = args.task_id_pattern

# -----------------------------
# Step 1: Poll Flower and Upsert into MongoDB
# -----------------------------
print("📡 Polling Flower for tasks...")
response = requests.get(FLOWER_TASK_API)
if response.status_code != 200:
    print("❌ Failed to fetch tasks from Flower.")
    exit(1)

tasks = response.json()
print(f"🔄 {len(tasks)} tasks found in Flower.")

mongo_client = MongoClient(MONGO_URI)
db = mongo_client[MONGO_DB]
collection = db[MONGO_COLLECTION]

for k, v in tasks.items():
    doc = {"_id": k, "value": v}
    result = collection.update_one({"_id": k}, {"$set": doc}, upsert=True)
    action = "Upserted" if result.upserted_id else "Updated"
    print(f"{action} task {k}")

# -----------------------------
# Step 2: Query MongoDB for Matching Tasks
# -----------------------------
print("🔍 Querying MongoDB for task ID pattern...")
query = {"value.result": {"$regex": re.compile(pattern)}}
flower_keys = ["uuid", "name", "state", "received", "started", "succeeded"]

flower_docs = []
for doc in tqdm(collection.find(query)):
    task_info = doc.get("value", {})
    filtered = {k: task_info.get(k) for k in flower_keys}
    flower_docs.append(prefix_keys(filtered, "flower"))
print(f"✅ Found {len(flower_docs)} matching tasks.")

# -----------------------------
# Step 3: Fetch Celery Worker Results
# -----------------------------
celery_app = Celery(broker=REDIS_BROKER, backend=REDIS_BACKEND)

print("📥 Fetching Celery results...")
worker_keys = ["chart_name", "log_id", "phase", "status", "run_id", "task_id", "task_name", "errors", "meta"]
result_keys = ["source", "type"]

combined_records = []
for flower_doc in flower_docs:
    task_id = flower_doc.get("flower_uuid")
    try:
        result = AsyncResult(task_id, app=celery_app)
        if not result.ready():
            print(f"⏭️ Task {task_id} not ready (state={result.state}), skipping.")
            continue
        result = result.result
    except Exception as e:
        print(f"❌ Error fetching result for {task_id}: {e}")
        continue

    result["errors"] = clean_list(result.get("errors", ""))
    result["meta"] = json.dumps(result.get("meta", {}))
    worker_payload = {k: result.get(k) for k in worker_keys}
    result_filtered = {k: result.get("result", {}).get(k) for k in result_keys} if result.get("result") else {}

    combined = {
        **flower_doc,
        **prefix_keys(worker_payload, "worker"),
        **prefix_keys(result_filtered, "result"),
    }
    combined_records.append(combined)
print(f"✅ Fetched results for {len(combined_records)} tasks.")

# -----------------------------
# Step 4: Format and Write to PostgreSQL
# -----------------------------
df = pd.DataFrame(combined_records)

for ts_col in ["flower_received", "flower_started", "flower_succeeded"]:
    if ts_col in df.columns:
        df[ts_col] = pd.to_datetime(df[ts_col], unit='s', errors='coerce')

df = df.sort_values(by=["worker_log_id", "worker_chart_name", "flower_received"])

final_columns = [
    "flower_uuid", "flower_received", "flower_succeeded","worker_run_id", "worker_task_id", "worker_log_id", "worker_chart_name",
    "worker_task_name", "worker_status", "worker_phase", "result_source", "result_type", "worker_errors"
]
df = df[final_columns]

print("🛢 Connecting to PostgreSQL...")
engine = create_engine(POSTGRES_URI)
existing_run_ids = pd.read_sql_table(POSTGRES_TABLE, engine, columns=["worker_run_id"])["worker_run_id"].tolist()

df = df[~df["worker_run_id"].isin(existing_run_ids)]
if df.empty:
    print("📭 No new data to insert.")
else:
    df.to_sql(POSTGRES_TABLE, engine, if_exists="append", index=False)
    print(f"✅ Inserted {len(df)} new records into PostgreSQL.")
