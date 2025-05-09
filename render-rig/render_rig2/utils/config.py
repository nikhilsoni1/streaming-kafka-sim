import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB_BROKER = os.getenv("REDIS_DB_BROKER", "0")
REDIS_DB_BACKEND = os.getenv("REDIS_DB_BACKEND", "1")

CELERY_CONFIG = {
    "broker_url": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_BROKER}",
    "result_backend": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_BACKEND}",
    "task_default_queue": "default",
    "worker_prefetch_multiplier": 1,
    "task_routes": {
        "lookup_chart_registry": {"queue": "lookup_chart_registry"},
        "get_existing_chart": {"queue": "get_existing_chart"},
        "lookup_log_registry": {"queue": "lookup_log_registry"},
        "get_log_dispatch_chart": {"queue": "get_log_dispatch_chart"},
        "store_chart_json_in_s3": {"queue": "store_log_chart"},
        "log_chart_in_registry": {"queue": "store_log_chart"},
    }
}
