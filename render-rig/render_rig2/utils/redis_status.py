# task_status.py (standalone)
import os
import json
import redis
from typing import Optional
from render_rig2.utils.logger import logger

# Global shared connection pool (singleton per process)
pool = redis.ConnectionPool(
    host=os.getenv("TASK_STATUS_REDIS_HOST"),
    port=int(os.getenv("TASK_STATUS_REDIS_PORT")),
    db=int(os.getenv("TASK_STATUS_REDIS_DB")),
    decode_responses=True,
    max_connections=100,
)

shared_redis = redis.Redis(connection_pool=pool)

def set_task_status(task_id: str, status_dict: dict, ttl_seconds: int = 120) -> None:
    try:
        result = shared_redis.setex(task_id, ttl_seconds, json.dumps(status_dict))
        logger.info(f"[{task_id}] Task status set: {result}")
        if not result:
            raise Exception("Redis setex returned False")
    except Exception as e:
        print(f"[ERROR] Failed to write task status: {e}")

def get_task_status(task_id: str) -> Optional[dict]:
    try:
        data = shared_redis.get(task_id)
        return json.loads(data) if data else None
    except Exception as e:
        print(f"[ERROR] Failed to read task status: {e}")
        return None
