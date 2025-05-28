import os
import json
import redis
from typing import Optional, Dict, Any


def get_redis_conn() -> redis.Redis:
    host = "localhost"
    port = 6379
    db=1
    decode = os.getenv("TASK_STATUS_REDIS_DECODE_RESPONSES", "true").lower() == "true"
    return redis.Redis(host=host, port=port, db=db, decode_responses=decode)


def fetch_key_value(r: redis.Redis, key: str) -> Optional[Any]:
    """Fetch the value of a key based on its Redis type."""
    key_type = r.type(key)
    
    if isinstance(key_type, bytes):
        key_type = key_type.decode()
        
    try:
        if key_type == 'string':
            return r.get(key)
        elif key_type == 'hash':
            return r.hgetall(key)
        elif key_type == 'list':
            return r.lrange(key, 0, -1)
        elif key_type == 'set':
            return list(r.smembers(key))  # Convert to list for JSON safety
        elif key_type == 'zset':
            return r.zrange(key, 0, -1, withscores=True)
        else:
            return f"<unsupported type: {key_type}>"
    except Exception as e:
        return f"<error: {str(e)}>"


def get_all_keys_and_values() -> Dict[str, Any]:
    """Connect to Redis and retrieve all keys and values."""
    r = get_redis_conn()
    result = {}

    for key in r.scan_iter("*"):  # scalable alternative to keys('*')
        result[key] = fetch_key_value(r, key)

    return result


if __name__ == "__main__":
    data = get_all_keys_and_values()
    print(json.dumps(data, indent=4, sort_keys=True))
