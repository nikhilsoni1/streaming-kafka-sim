import re
import json
import pandas as pd
from pymongo import MongoClient
from celery import Celery
from celery.result import AsyncResult
from sqlalchemy import create_engine
from uuid import uuid4
import hashlib
from tqdm import tqdm

# -----------------------------
# Configuration
# -----------------------------
MONGO_URI = "mongodb://localhost:27017"
MONGO_DB = "render-rig2-tasks"
MONGO_COLLECTION = "group1"
TASK_ID_PATTERN = "30632fc9-4b03-415e-86fe-2445d5897c9b"
REDIS_BROKER = "redis://localhost:6379/0"
REDIS_BACKEND = "redis://localhost:6379/1"

POSTGRES_URI = "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"
POSTGRES_TABLE = "control"

# -----------------------------
# Utilities
# -----------------------------
def prefix_keys(payload, prefix):
    return {f"{prefix}_{k}": v for k, v in payload.items()}

def clean_list(lst):
    """Strip whitespace and \n from list items, join with '; '."""
    return "; ".join(str(item).strip().replace("\n", " ") for item in lst if item).strip()


def sha256_of_dataframe(df: pd.DataFrame) -> str:
    """
    Compute a SHA-256 hash of a Pandas DataFrame.
    Ensures consistent ordering and formatting before hashing.

    Parameters:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        str: A SHA-256 hash string of the DataFrame.
    """
    # Sort by column names to ensure consistent column order
    df_sorted = df.sort_index(axis=1).sort_values(by=df.columns.tolist()).reset_index(drop=True)

    # Convert to CSV bytes for a stable string representation
    csv_bytes = df_sorted.to_csv(index=False).encode("utf-8")

    # Compute SHA-256
    return hashlib.sha256(csv_bytes).hexdigest()

# -----------------------------
# Setup Clients
# -----------------------------
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[MONGO_DB]
collection = db[MONGO_COLLECTION]

celery_app = Celery(broker=REDIS_BROKER, backend=REDIS_BACKEND)

# -----------------------------
# Step 1: Query MongoDB
# -----------------------------

print("🔍 Querying MongoDB for tasks...")
query = {"value.result": {"$regex": re.compile(TASK_ID_PATTERN)}}
flower_keys = ["uuid", "name", "state", "received", "started", "succeeded"]

flower_docs = []
for doc in tqdm(collection.find(query)):
    task_info = doc.get("value", {})
    filtered = {k: task_info.get(k) for k in flower_keys}
    flower_docs.append(prefix_keys(filtered, "flower"))
print(f"Found {len(flower_docs)} tasks matching the pattern '{TASK_ID_PATTERN}'.")
# -----------------------------
# Step 2: Fetch Celery Worker Results
# -----------------------------
print("🔄 Fetching results from Celery workers...")
worker_keys = ["chart_name", "log_id", "phase", "status", "run_id","task_id", "task_name", "errors", "meta"]
result_keys = ["source", "type"]

combined_records = []

for flower_doc in flower_docs:
    task_id = flower_doc.get("flower_uuid")
    try:
        print(f"Fetching result for task {task_id}...")
        result = AsyncResult(task_id, app=celery_app)
        if not result.ready():
            print(f"⏭️ Task {task_id} not ready (state={result.state}), skipping.")
            continue

        result = result.result
    except Exception as e:
        print(f"Failed to fetch result for task {task_id}: {e}")
        continue

    # Clean and prefix worker payload
    result["errors"] = clean_list(result.get("errors", ""))
    result["meta"] = json.dumps(result.get("meta", {}))
    worker_payload = {k: result.get(k) for k in worker_keys}
    worker_result = result.get("result", {})
    result_filtered = {k: worker_result.get(k) for k in result_keys} if worker_result else {}

    combined = {
        **flower_doc,
        **prefix_keys(worker_payload, "worker"),
        **prefix_keys(result_filtered, "result")
    }
    combined_records.append(combined)
print(f"Fetched results for {len(combined_records)} tasks.")
# -----------------------------
# Step 3: Create and Format DataFrame
# -----------------------------
print("📊 Creating DataFrame from combined records...")
final_columns = [
    "flower_uuid", "flower_received", "worker_run_id", "worker_task_id", "worker_log_id", "worker_chart_name",
    "worker_task_name", "worker_status", "worker_phase",
    "result_source", "result_type", "worker_errors"
]

df = pd.DataFrame(combined_records)

# Convert timestamps
for ts_col in ["flower_received", "flower_started", "flower_succeeded"]:
    if ts_col in df.columns:
        df[ts_col] = pd.to_datetime(df[ts_col], unit='s', errors='coerce')

df = df.sort_values(by=["worker_log_id", "worker_chart_name", "flower_received"])
df = df[final_columns]
# -----------------------------
# Step 4: Write to PostgreSQL
# -----------------------------
print("🚀 Connecting to PostgreSQL")
engine = create_engine(POSTGRES_URI)
print("✅ Connected. Writing to DB...")



# ignore inserting to postgres if group_id already exists
existing_run_ids = pd.read_sql_table(POSTGRES_TABLE, engine, columns=["worker_run_id"])["worker_run_id"].tolist()
df = df[~df["worker_run_id"].isin(existing_run_ids)]
if df.empty:
    print("No new data to write to PostgreSQL.")
    exit()
df.to_sql(POSTGRES_TABLE, engine, if_exists="append", index=False)
print("✅ Write complete.")
