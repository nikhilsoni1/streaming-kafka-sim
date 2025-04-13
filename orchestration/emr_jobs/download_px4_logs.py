from pyspark.sql import SparkSession
from db.core.database import DatabaseClient
from db.repositories.registry import LogDlRepository
from pprint import pprint
from uuid import uuid4
import datetime

def download_log(log_record, bucket="flight-px4-logs", download_api="https://review.px4.io/download"):
    # imports
    import boto3
    from uuid import uuid4
    import hashlib
    import datetime
    import requests
    from urllib3.response import HTTPResponse

    # get log_id from log_record
    log_id = log_record['log_id']

    # create filename and filepath
    log_day = log_record['log_day']
    log_month = log_record['log_month']
    log_year = log_record['log_year']
    log_filename = f"file_{uuid4().hex}"
    log_s3_key = f"raw-logs/{log_year}/{log_month}/{log_day}/{log_filename}.ulg"

    # initiate file size and hash variables
    file_size_bytes = 0
    file_sha256 = hashlib.sha256()

    # create url to download log from download_api
    url = f"{download_api}?log={log_id}"

    client = boto3.client('s3')

    # request and stream upload
    upload_status = "failed"  # default to failed
    try:
        with requests.get(url, stream=True, timeout=10 * 60) as response:
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
            client.upload_fileobj(stream, bucket, log_s3_key)
            upload_status = "succeeded"

    except Exception as e:
        print(f"Upload failed for log_id={log_id}: {e}")

    # prepare log record for upload
    log_dict = {
        "job_id": log_record['job_id'],
        "upd_ts_utc": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S"),
        "log_id": log_id,
        "status": upload_status,
        "file_s3_path": f"s3://{bucket}/{log_s3_key}" if upload_status == "succeeded" else None,
        "file_name": log_filename,
        "file_ext": "ulg",
        "file_size_bytes": file_size_bytes if upload_status == "succeeded" else None,
        "file_sha256": file_sha256.hexdigest() if upload_status == "succeeded" else None,
        "stdout": None,
        "stderr": None
    }
    return log_dict

# fetch env variables
DATABASE_USER="moffett_blvd"
DATABASE_PASSWORD="RFM_analysis_2025"
DATABASE_HOST="elephant01.cizii2a86p9h.us-east-1.rds.amazonaws.com"
DATABASE_PORT=5432
DATABASE_NAME="px4"


# initialize database client
dbclient = DatabaseClient(
    database_user=DATABASE_USER,
    database_password=DATABASE_PASSWORD,
    database_host=DATABASE_HOST,
    database_port=DATABASE_PORT,
    database_name=DATABASE_NAME,
)
session = dbclient.get_session()

# initialize repository and fetch log entries
repo = LogDlRepository(session)

# fetch new log entries
r = repo.get_new_log_entries(limit=3)

# generate job_id and timestamp for this job
job_id = str(uuid4())
log_ts_utc = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S")

# prepare log_ids and update records
log_ids = list()
for record in r:
    log_ids.append(record['log_id'])
    record["job_id"] = job_id

# insert log_ids into registry, mark as in_process
repo.insert_logs_in_process(log_ids, job_id=job_id, log_ts_utc=log_ts_utc)

# write spark logic

# start a spark session
spark = SparkSession.builder.appName("LogIDTest").getOrCreate()
sc = spark.sparkContext

# create RDD from log_ids
num_slices = max(1, len(log_ids) // 2)
rdd = sc.parallelize(log_ids, numSlices=num_slices)

# trigger action to run tasks
collect_list = rdd.map(download_log).collect()

collect_list = list()
for record in r:
    log_dict = download_log(record)
    collect_list.append(log_dict)

repo.update_logs_by_job_and_log_id(collect_list)

session.close()




