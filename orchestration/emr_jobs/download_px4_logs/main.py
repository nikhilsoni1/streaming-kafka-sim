from pyspark.sql import SparkSession
from db.core.database import DatabaseClient
from db.repositories.registry import LogDlRepository
from uuid import uuid4
import datetime
import os

# Constants
BUCKET = "flight-px4-logs"
DOWNLOAD_API = "https://review.px4.io/download"

# Fetch environment variables
# load from environment variables, do not put in defaults
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = int(os.getenv("DATABASE_PORT", 5432))
DATABASE_NAME = os.getenv("DATABASE_NAME")
JOB_ID = os.getenv("JOB_ID", str(uuid4()))

_now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H:%M:%S")
# Spark initialization
spark = SparkSession.builder.appName(f"PX4LogDownloader-{JOB_ID}").getOrCreate()
sc = spark.sparkContext

# Step 1: Setup DB client and fetch log records
dbclient = DatabaseClient(
    database_user=DATABASE_USER,
    database_password=DATABASE_PASSWORD,
    database_host=DATABASE_HOST,
    database_port=DATABASE_PORT,
    database_name=DATABASE_NAME,
)
session = dbclient.get_session()
repo = LogDlRepository(session)

# Fetch logs to process
records = repo.get_new_log_entries(limit=50)  # Increase this as needed
job_id = JOB_ID
log_ts_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

# Assign job_id
for record in records:
    record["job_id"] = job_id

log_ids = [r["log_id"] for r in records]
repo.insert_logs_in_process(log_ids, job_id=job_id, log_ts_utc=log_ts_utc)

# Step 2: Define partition download function
def download_and_upload_partition(log_records_iter):
    import boto3
    import hashlib
    import requests
    from uuid import uuid4
    import datetime
    import logging

    client = boto3.client("s3")
    results = []

    for log_record in log_records_iter:
        log_id = log_record["log_id"]
        log_day = log_record["log_day"]
        log_month = log_record["log_month"]
        log_year = log_record["log_year"]
        log_filename = f"file_{uuid4().hex}"
        log_s3_key = f"raw-logs/{log_year}/{log_month}/{log_day}/{log_filename}.ulg"
        file_size_bytes = 0
        file_sha256 = hashlib.sha256()
        upload_status = "failed"
        url = f"{DOWNLOAD_API}?log={log_id}"

        try:
            with requests.get(url, stream=True, timeout=600) as response:
                response.raise_for_status()

                class HashingStream:
                    def __init__(self, raw):
                        self.raw = raw

                    def read(self, amt=1024):
                        chunk = self.raw.read(amt)
                        if chunk:
                            nonlocal file_size_bytes
                            file_size_bytes += len(chunk)
                            file_sha256.update(chunk)
                        return chunk

                stream = HashingStream(response.raw)
                client.upload_fileobj(stream, BUCKET, log_s3_key)
                upload_status = "succeeded"

        except Exception as e:
            logging.warning(f"Upload failed for log_id={log_id}: {e}")

        results.append({
            "job_id": log_record["job_id"],
            "upd_ts_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "log_id": log_id,
            "status": upload_status,
            "file_s3_path": f"s3://{BUCKET}/{log_s3_key}" if upload_status == "succeeded" else None,
            "file_name": log_filename,
            "file_ext": "ulg",
            "file_size_bytes": file_size_bytes if upload_status == "succeeded" else None,
            "file_sha256": file_sha256.hexdigest() if upload_status == "succeeded" else None,
            "stdout": None,
            "stderr": None
        })

    return iter(results)

# Step 3: Distribute and run the download/upload tasks
numSlices = max(1, len(records) // 2)
rdd = sc.parallelize(records, numSlices=numSlices)
results_rdd = rdd.mapPartitions(download_and_upload_partition)
results = results_rdd.collect()

# Step 4: Update DB with results
repo.update_logs_by_job_and_log_id(results)

# Final cleanup
session.close()
spark.stop()
