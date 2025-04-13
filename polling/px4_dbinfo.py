import requests
import hashlib
import json
from datetime import datetime, timezone
import os
import base64
import redis
import re
from uuid import uuid4
from pprint import pprint

from db.database import SessionLocal
from db.repositories.dbinfo import RawDbinfoRepository

DEFAULT_CONTROL_CHAR_RE = re.compile(r'[\x00-\x1F]+')

def replace_control_chars(obj, replacement='[__BAD_CHAR__]', control_char_re=DEFAULT_CONTROL_CHAR_RE):
    """
    Recursively replaces ASCII control characters in strings with a replacement token.
    Allows a custom regex to be passed in.
    """
    if isinstance(obj, dict):
        return {k: replace_control_chars(v, replacement, control_char_re) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_control_chars(v, replacement, control_char_re) for v in obj]
    elif isinstance(obj, str):
        return control_char_re.sub(replacement, obj)
    return obj

def get_current_utc_time():
    """Returns the current UTC time as a string."""
    current_utc_time = datetime.now(timezone.utc)
    current_utc_time = current_utc_time.replace(tzinfo=None)
    current_utc_time_str = current_utc_time.strftime('%Y-%m-%d %H:%M:%S')
    return current_utc_time_str

def get_cached_json(redis_client, url, ttl=28800, bypass_cache=False):
    key = f"url_cache:{hashlib.sha256(url.encode()).hexdigest()}"
    if not bypass_cache:
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

def fetch_and_store(redis_client, url, ttl=36000, **kwargs):
    bypass_cache = kwargs.get('bypass_cache', False)
    print(f"Fetching data from API with Redis cache... {url}")
    raw_json = get_cached_json(redis_client, url, ttl=ttl, bypass_cache=bypass_cache)

    # Compute hash from the raw JSON
    raw_json_str = json.dumps(raw_json, sort_keys=True)
    encoded_json = base64.b64encode(raw_json_str.encode("utf-8")).decode("utf-8")
    # hash_sha256 = hashlib.sha256(encoded_json.encode("utf-8")).hexdigest()
    # Clean the raw JSON before storing
    cleaned_json = replace_control_chars(raw_json)
    log_ts_utc = get_current_utc_time()
    job_id = str(uuid4())
    records_list = list()
    session = SessionLocal()
    repo = RawDbinfoRepository(session=session)
    for ctr, record in enumerate(cleaned_json):
        record['job_id'] = job_id
        record['log_ts_utc'] = log_ts_utc
        records_list.append(record.copy())
    repo.write_records(records_list, use_tqdm=True)
    session.close()
    print(f"Fetched {len(records_list)} records.")

        
        


if __name__ == '__main__':
    url = "https://review.px4.io/dbinfo"
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    fetch_and_store(redis_client, url=url, bypass_cache=False)