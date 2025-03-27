import requests
import hashlib
import json
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import JSONB
import os
import base64
import redis

# Load environment variables
postgres_user = os.environ['POSTGRES_USER']
postgres_password = os.environ['POSTGRES_PASSWORD']
postgres_host = os.environ['POSTGRES_HOST']
postgres_port = os.environ['POSTGRES_PORT']
postgres_db = os.environ['POSTGRES_DB']

DATABASE_URL = (
    f"postgresql://{postgres_user}:{postgres_password}"
    f"@{postgres_host}:{postgres_port}/{postgres_db}"
)

engine = sa.create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Define table metadata
metadata = sa.MetaData(schema="dbinfo")

raw_dbinfo = sa.Table(
    "raw_dbinfo",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("log_ts_utc", sa.DateTime()),
    sa.Column("hash_sha256", sa.Text, unique=True),
    sa.Column("raw_json", JSONB),
)

# API URL
URL = "https://review.px4.io/dbinfo"

def get_current_utc_time():
    """Returns the current UTC time as a string."""
    current_utc_time = datetime.now(timezone.utc)
    current_utc_time = current_utc_time.replace(tzinfo=None)
    current_utc_time_str = current_utc_time.strftime('%Y-%m-%d %H:%M:%S')
    return current_utc_time_str

def get_cached_json(redis_client, url, ttl=3600):
    key = f"url_cache:{hashlib.sha256(url.encode()).hexdigest()}"
    cached = redis_client.get(key)
    if cached:
        print("From cache")
        return json.loads(cached)
    print("Fetching from URL...")
    resp = requests.get(url)
    resp.raise_for_status()
    json_data = resp.json()
    redis_client.setex(key, ttl, json.dumps(json_data))
    return json_data

def fetch_and_store(redis_client, ttl=3600):
    session = Session()
    try:
        print(f"Fetching data from API with Redis cache... {URL}")
        raw_json = get_cached_json(redis_client, URL, ttl=ttl)
        json_str = json.dumps(raw_json, sort_keys=True)

        encoded_json = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        hash_sha256 = hashlib.sha256(encoded_json.encode('utf-8')).hexdigest()

        exists = session.query(raw_dbinfo).filter_by(hash_sha256=hash_sha256).first()
        if exists:
            print("No new data, skipping insert.")
        else:
            insert_stmt = raw_dbinfo.insert().values(
                log_ts_utc=get_current_utc_time(),
                hash_sha256=hash_sha256,
                raw_json=encoded_json
            )
            session.execute(insert_stmt)
            session.commit()
            print("New data inserted successfully.")

    except requests.HTTPError as http_err:
        print(f"HTTP error: {http_err}")
    except Exception as err:
        print(f"Unexpected error: {err}")
    finally:
        session.close()

if __name__ == '__main__':
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    fetch_and_store(redis_client, ttl=3600)
