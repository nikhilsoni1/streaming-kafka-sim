from pyspark.sql import SparkSession
from db.core.database import DatabaseClient
from db.repositories.registry import LogDlRepository
from uuid import uuid4
from pprint import pprint
import datetime
import boto3
import json
import logging
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("log-entry-fetcher")

DATABASE_CONFIG = {
    "database_user": os.environ.get("DATABASE_USER"),
    "database_password": os.environ.get("DATABASE_PASSWORD"),
    "database_host": os.environ.get("DATABASE_HOST"),
    "database_port": int(os.environ.get("DATABASE_PORT", 5432)),
    "database_name": os.environ.get("DATABASE_NAME"),
}

S3_BUCKET = "flight-px4-logs"
S3_KEY = "test/db_q.json"


def fetch_new_log_entries(limit=3):
    """Fetch new log entries from the DB and return them as a dictionary."""
    dbclient = DatabaseClient(**DATABASE_CONFIG)
    session = dbclient.get_session()
    repo = LogDlRepository(session)

    try:
        logger.info("Fetching log entries from the database...")
        logs = repo.get_new_log_entries(limit=limit)
        result = {
            "log_entries": logs,
            "log_ts_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        }
        logger.info(f"Fetched {len(logs)} log entries.")
        return result
    finally:
        session.close()
        logger.info("Database session closed.")


def upload_to_s3(data: dict, bucket: str, key: str):
    """Upload JSON data to the specified S3 bucket."""
    s3 = boto3.client("s3")
    try:
        logger.info(f"Uploading data to s3://{bucket}/{key} ...")
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(data, indent=4, sort_keys=True).encode("utf-8"),
        )
        logger.info("✅ Successfully uploaded data to S3.")
    except Exception as e:
        logger.error(f"❌ Failed to upload to S3: {e}")
        raise


if __name__ == "__main__":

    try:
        logger.info("🚀 Starting log fetch and upload job.")
        result = fetch_new_log_entries(limit=3)
        upload_to_s3(result, S3_BUCKET, S3_KEY)
    except Exception as err:
        logger.exception(f"Unhandled error occurred: {err}")
        sys.exit(1)

    logger.info("🎯 Job completed successfully.")
    spark = SparkSession.builder.appName("LogUploader").getOrCreate()
    spark.range(1).collect()  # Dummy job to keep Spark happy
    spark.stop()
    sys.exit(0)
