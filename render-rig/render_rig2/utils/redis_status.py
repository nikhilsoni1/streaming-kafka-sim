import os
import json
import redis
from typing import Optional

def get_redis_conn() -> redis.Redis:
    host = os.getenv("TASK_STATUS_REDIS_HOST")
    port = int(os.getenv("TASK_STATUS_REDIS_PORT", 6379))
    db = int(os.getenv("TASK_STATUS_REDIS_DB", 0))
    return redis.Redis(host=host, port=port, db=db)

def set_task_status(task_id: str, status_dict: dict, ttl_seconds: int = 120) -> None:
    r = get_redis_conn()
    r.setex(task_id, ttl_seconds, json.dumps(status_dict))

def get_task_status(task_id: str) -> Optional[dict]:
    r = get_redis_conn()
    data = r.get(task_id)
    if data:
        return json.loads(data)
    return None
