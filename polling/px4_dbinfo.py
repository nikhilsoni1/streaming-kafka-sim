import requests
import hashlib
import json
from datetime import datetime, timezone
import os
import base64
import redis
import re

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

def fetch_and_store(redis_client, url, ttl=3600):
    session = SessionLocal()
    try:
        print(f"Fetching data from API with Redis cache... {url}")
        raw_json = get_cached_json(redis_client, url, ttl=ttl)

        # Compute hash from the raw JSON
        raw_json_str = json.dumps(raw_json, sort_keys=True)
        encoded_json = base64.b64encode(raw_json_str.encode("utf-8")).decode("utf-8")
        hash_sha256 = hashlib.sha256(encoded_json.encode("utf-8")).hexdigest()

        # Clean the raw JSON before storing
        cleaned_json = replace_control_chars(raw_json)

        # Insert into DB using repository
        repo = RawDbinfoRepository(session)
        repo.insert(
            log_ts_utc=get_current_utc_time(),
            hash_sha256=hash_sha256,
            raw_json=cleaned_json,
            raw_json_b64=encoded_json,
        )
        print("New data inserted successfully.")

    except requests.HTTPError as http_err:
        print(f"HTTP error: {http_err}")
    except Exception as err:
        print(f"Unexpected error: {err}")
    finally:
        session.close() 
if __name__ == '__main__':
    url = "https://review.px4.io/dbinfo"
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    fetch_and_store(redis_client, url=url, ttl=3600)